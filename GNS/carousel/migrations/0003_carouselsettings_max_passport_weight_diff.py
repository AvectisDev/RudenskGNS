from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carousel', '0002_carouselsettings_carousel_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='carouselsettings',
            name='max_passport_weight_diff',
            field=models.FloatField(
                default=21.5,
                verbose_name='Максимальная разница в паспортных весах баллона',
            ),
        ),
    ]
