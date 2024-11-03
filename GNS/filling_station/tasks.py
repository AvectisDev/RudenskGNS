from celery import shared_task
from .management.commands.generate_1C_file import Command


@shared_task
def generate_1c_file():
    command = Command()
    command.handle()
