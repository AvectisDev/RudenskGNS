# Make number required and unique; drop legacy carousel_number

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carousel', '0006_populate_carouselsettings_instance_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carouselsettings',
            name='number',
            field=models.IntegerField(
                unique=True,
                verbose_name='Номер карусели',
            ),
        ),
        migrations.RemoveField(
            model_name='carouselsettings',
            name='carousel_number',
        ),
    ]
