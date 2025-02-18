import logging
from celery import shared_task
from django.core.management import call_command
from .management.commands.generate_1C_file import Command as Generate1CFileCommand
from .management.commands.railway_tank import Command as RailwayTankHandleCommand
from .management.commands.auto_gas_batch import Command as AutoGasBatchHandleCommand
from .management.commands.railway_batch import Command as RailwayBatchHandleCommand

logger = logging.getLogger('filling_station')

@shared_task
def send_to_opc(reader, blink):
    # logger.info('таска send_to_opc выполняется...')
    call_command('send_to_opc', reader=reader, blink=blink)

@shared_task
def generate_1c_file():
    command = Generate1CFileCommand()
    command.handle()

@shared_task
def railway_tank_processing():
    command = RailwayTankHandleCommand()
    logger.info('Начало обработки жд цистерн...')
    command.handle()

@shared_task
def railway_batch_processing():
    command = RailwayBatchHandleCommand()
    logger.info('Проверка активных партий...')
    command.handle()

@shared_task
def auto_gas_processing():
    command = AutoGasBatchHandleCommand()
    logger.info('Начало обработки автоцистерн...')
    command.handle()