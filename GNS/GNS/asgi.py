import os
import sys
import signal
import subprocess

# Глобальный список процессов
processes = []

def start_processes():
    """Запускаем дочерние процессы и сохраняем их объекты."""
    global processes
    print('Starting processes...')

    python = sys.executable
    p1 = subprocess.Popen([
        python,
        '-m',
        'filling_station.management.commands.rfid_utils.feig_protocol',
    ])
    p2 = subprocess.Popen([
        python,
        '-m',
        'carousel.management.commands.carousel.main',
    ])
    processes.extend([p1, p2])
    print(f'Processes is started: {processes}')

def stop_processes():
    """Завершаем дочерние процессы."""
    print('Stopping processes...')
    for p in processes:
        try:
            p.terminate()
        except Exception as e:
            print(f'Error while stopping processes: {e}')
    for p in processes:
        try:
            p.wait(timeout=10)
        except subprocess.TimeoutExpired:
            print('The process did not complete within the allotted time. kill')
            p.kill()

def handle_exit(signum, frame):
    """Обработчик сигнала для корректной остановки."""
    stop_processes()
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

start_processes()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GNS.settings')
from django.core.asgi import get_asgi_application

application = get_asgi_application()
