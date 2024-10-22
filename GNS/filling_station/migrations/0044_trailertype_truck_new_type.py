# Generated by Django 5.0.6 on 2024-10-22 10:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('filling_station', '0043_trucktype_remove_balloon_insert_insert_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrailerType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=50, verbose_name='Тип прицепа')),
            ],
            options={
                'verbose_name': 'Тип прицепа',
                'verbose_name_plural': 'Типы прицепов',
            },
        ),
        migrations.AddField(
            model_name='truck',
            name='new_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='filling_station.trucktype', verbose_name='Тип'),
        ),
    ]
