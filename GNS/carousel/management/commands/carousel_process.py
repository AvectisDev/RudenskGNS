from django.core.management.base import BaseCommand
import subprocess
import os


class Command(BaseCommand):
    help = 'Запуск main.py - приложения обработки данных с постов наполнения УНБ'

    def handle(self, *args, **kwargs):
        carousels = [
            {'number': 1, 'port': 'COM3', 'reader': 8},
            {'number': 2, 'port': 'COM4', 'reader': 9},
            {'number': 3, 'port': 'COM5', 'reader': 10},
        ]

        for carousel in carousels:
            env = os.environ.copy()
            env['CAROUSEL_NUMBER'] = str(carousel['number'])
            env['CAROUSEL_COM_PORT'] = carousel['port']
            env['CAROUSEL_READER_NUMBER'] = str(carousel['reader'])

            custom_api_host = os.environ.get(f'CAROUSEL_{carousel["number"]}_API_HOST')
            if custom_api_host:
                env['CAROUSEL_API_HOST'] = custom_api_host

            subprocess.Popen(
                ['python', '-m', 'carousel.management.commands.carousel.main'],
                env=env
            )
