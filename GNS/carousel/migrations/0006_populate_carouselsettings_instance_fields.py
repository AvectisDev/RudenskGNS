# Data migration: map carousel_number -> number, ensure rows 1-3, apply env

import os

from django.db import migrations

DEFAULT_RFID_READERS = {
    1: '8',
    2: '9',
    3: '10',
}


def _resolve_reader(ReaderSettings, reader_number_raw):
    if not reader_number_raw:
        return None
    try:
        return ReaderSettings.objects.filter(
            number=int(reader_number_raw)
        ).first()
    except (TypeError, ValueError):
        return None


def populate_carousel_settings(apps, schema_editor):
    CarouselSettings = apps.get_model('carousel', 'CarouselSettings')
    ReaderSettings = apps.get_model('filling_station', 'ReaderSettings')

    for settings in CarouselSettings.objects.all():
        if settings.number is None:
            settings.number = settings.carousel_number
        if not settings.name:
            settings.name = f'Карусель {settings.number}'
        settings.save()

    existing_numbers = set(
        CarouselSettings.objects.exclude(number__isnull=True)
        .values_list('number', flat=True)
    )
    for carousel_number in (1, 2, 3):
        if carousel_number not in existing_numbers:
            CarouselSettings.objects.create(
                carousel_number=carousel_number,
                number=carousel_number,
                name=f'Карусель {carousel_number}',
                is_active=False,
                user=None,
            )

    for carousel_number in (1, 2, 3):
        settings = CarouselSettings.objects.get(number=carousel_number)
        env_prefix = f'CAROUSEL_{carousel_number}'

        tcp_host = os.getenv(f'{env_prefix}_TCP_HOST', '').strip()
        if tcp_host:
            settings.tcp_host = tcp_host

        tcp_port_raw = os.getenv(f'{env_prefix}_TCP_PORT', '').strip()
        if tcp_port_raw:
            try:
                settings.tcp_port = int(tcp_port_raw)
            except (TypeError, ValueError):
                pass

        reader_number_raw = os.getenv(
            f'{env_prefix}_RFID_READER',
            DEFAULT_RFID_READERS.get(carousel_number, ''),
        ).strip()
        reader = _resolve_reader(ReaderSettings, reader_number_raw)
        if reader is not None:
            settings.rfid_reader = reader

        if not settings.name:
            settings.name = f'Карусель {carousel_number}'

        settings.save()


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('carousel', '0005_carouselsettings_per_instance_fields'),
    ]

    operations = [
        migrations.RunPython(populate_carousel_settings, noop_reverse),
    ]
