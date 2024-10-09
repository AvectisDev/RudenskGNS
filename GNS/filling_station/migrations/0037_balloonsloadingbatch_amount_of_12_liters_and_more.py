# Generated by Django 5.0.6 on 2024-10-09 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('filling_station', '0036_rename_number_railwaytank_registration_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='balloonsloadingbatch',
            name='amount_of_12_liters',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='Количество 12л баллонов'),
        ),
        migrations.AddField(
            model_name='balloonsunloadingbatch',
            name='amount_of_12_liters',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='Количество 12л баллонов'),
        ),
    ]
