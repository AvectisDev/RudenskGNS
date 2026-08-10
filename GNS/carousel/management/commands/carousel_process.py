import os
import subprocess
import sys
import time
from pathlib import Path

from django.core.management.base import BaseCommand


CAROUSEL_NUMBERS = (1, 2, 3)
RESTART_DELAY_SECONDS = 5
DJANGO_PROJECT_DIR = Path(__file__).resolve().parents[3]


def start_carousel(carousel_number: int) -> subprocess.Popen:
    env = os.environ.copy()
    env['CAROUSEL_NUMBER'] = str(carousel_number)
    return subprocess.Popen(
        [
            sys.executable,
            '-m',
            'carousel.management.commands.carousel.main',
        ],
        env=env,
        cwd=DJANGO_PROJECT_DIR,
    )


def run_carousels() -> None:
    processes = {
        number: start_carousel(number)
        for number in CAROUSEL_NUMBERS
    }

    try:
        while True:
            for number, process in tuple(processes.items()):
                if process.poll() is not None:
                    time.sleep(RESTART_DELAY_SECONDS)
                    processes[number] = start_carousel(number)
            time.sleep(1)
    finally:
        for process in processes.values():
            if process.poll() is None:
                process.terminate()
        for process in processes.values():
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()


class Command(BaseCommand):
    help = 'Запуск COM-процессов трёх каруселей наполнения'

    def handle(self, *args, **kwargs):
        run_carousels()


if __name__ == '__main__':
    run_carousels()
