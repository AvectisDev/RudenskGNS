from django.core.management.base import BaseCommand
import subprocess


class Command(BaseCommand):
    help = 'Запуск скрипта main.py приложения обработки RFID считывателей'

    def handle(self, *args, **kwargs):
        subprocess.Popen(['python', '../rfid app/main.py'])
