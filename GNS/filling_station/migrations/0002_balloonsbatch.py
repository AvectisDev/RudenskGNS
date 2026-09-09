import datetime

import django.db.models.deletion
from django.conf import settings
from django.core.management.color import no_style
from django.db import migrations, models
from django.utils import timezone


def _combine(date_value, time_value):
    if not date_value:
        return None
    value = datetime.datetime.combine(date_value, time_value or datetime.time.min)
    if settings.USE_TZ and timezone.is_naive(value):
        value = timezone.make_aware(value, timezone.get_current_timezone())
    return value


def _copy_batches(apps, schema_editor):
    BalloonsBatch = apps.get_model('filling_station', 'BalloonsBatch')
    Loading = apps.get_model('filling_station', 'BalloonsLoadingBatch')
    Unloading = apps.get_model('filling_station', 'BalloonsUnloadingBatch')

    common_fields = (
        'truck_id', 'trailer_id', 'reader_number', 'amount_of_rfid',
        'amount_of_5_liters', 'amount_of_12_liters', 'amount_of_27_liters',
        'amount_of_50_liters', 'gas_amount', 'user_id',
    )
    for source_model, batch_type, id_offset in (
        (Loading, 'l', 0),
        (Unloading, 'u', 1),
    ):
        for old in source_model.objects.all().iterator():
            values = {field: getattr(old, field) for field in common_fields}
            ttn_text = (old.ttn or '').strip()
            values.update(
                id=old.pk * 2 + id_offset,
                batch_type=batch_type,
                completed_at=_combine(old.end_date, old.end_time),
                status='active' if old.is_active else 'completed',
                amount_of_sensor=0,
                amount_of_ttn=old.amount_of_ttn or 0,
                ttn_id=int(ttn_text) if ttn_text.isdigit() else 0,
                balloons_type='e',
            )
            new = BalloonsBatch.objects.create(**values)
            BalloonsBatch.objects.filter(pk=new.pk).update(
                started_at=_combine(old.begin_date, old.begin_time)
            )
            new.balloon_list.set(old.balloon_list.all())

    statements = schema_editor.connection.ops.sequence_reset_sql(no_style(), [BalloonsBatch])
    with schema_editor.connection.cursor() as cursor:
        for statement in statements:
            cursor.execute(statement)


def _delete_copied_batches(apps, schema_editor):
    apps.get_model('filling_station', 'BalloonsBatch').objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('filling_station', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BalloonsBatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('batch_type', models.CharField(choices=[('l', 'Приёмка'), ('u', 'Отгрузка')], default='l', verbose_name='Тип партии')),
                ('started_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата и время начала')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='Дата и время окончания')),
                ('reader_number', models.IntegerField(blank=True, null=True, verbose_name='Номер считывателя')),
                ('amount_of_rfid', models.IntegerField(default=0, verbose_name='Количество баллонов по rfid')),
                ('amount_of_sensor', models.IntegerField(default=0, verbose_name='Количество баллонов по датчику')),
                ('amount_of_ttn', models.IntegerField(default=0, verbose_name='Количество баллонов по электронной ТТН')),
                ('amount_of_5_liters', models.IntegerField(default=0, verbose_name='Количество 5л баллонов')),
                ('amount_of_12_liters', models.IntegerField(default=0, verbose_name='Количество 12л баллонов')),
                ('amount_of_27_liters', models.IntegerField(default=0, verbose_name='Количество 27л баллонов')),
                ('amount_of_50_liters', models.IntegerField(default=0, verbose_name='Количество 50л баллонов')),
                ('gas_amount', models.FloatField(blank=True, null=True, verbose_name='Количество газа')),
                ('status', models.CharField(choices=[('active', 'В работе'), ('paused', 'Приостановлена'), ('completed', 'Завершена'), ('miriada_error', 'Завершена, ошибка Мириады')], db_index=True, default='paused', max_length=20, verbose_name='Статус партии')),
                ('miriada_close_failed', models.BooleanField(default=False, verbose_name='Ошибка закрытия ТТН в Мириаде')),
                ('miriada_error_message', models.CharField(blank=True, max_length=200, null=True, verbose_name='Текст ошибки при неудачном закрытии ТТН')),
                ('miriada_balloons_sent', models.BooleanField(default=False, verbose_name='Статусы баллонов отправлены в Мириаду')),
                ('ttn_id', models.IntegerField(default=0, verbose_name='ID ТТН')),
                ('balloons_type', models.CharField(choices=[('e', 'Пустой'), ('f', 'Полный')], default='e', verbose_name='Пустой/полный')),
                ('balloon_list', models.ManyToManyField(blank=True, to='filling_station.balloon', verbose_name='Список баллонов')),
                ('trailer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='filling_station.trailer', verbose_name='Прицеп')),
                ('truck', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='filling_station.truck', verbose_name='Автомобиль')),
                ('user', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Партия баллонов',
                'verbose_name_plural': 'Партии баллонов',
                'ordering': ['-started_at'],
            },
        ),
        migrations.RunPython(_copy_batches, _delete_copied_batches),
    ]
