# Generated by Django 5.0.6 on 2024-09-08 17:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('filling_station', '0028_alter_balloonsunloadingbatch_balloons_list'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='RailwayTanks',
            new_name='RailwayTank',
        ),
    ]
