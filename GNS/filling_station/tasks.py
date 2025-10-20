import logging
from celery import shared_task
from django.core.management import call_command

logger = logging.getLogger('celery')

@shared_task
def send_to_opc(reader, blink):
    # logger.info('таска send_to_opc выполняется...')
    call_command('send_to_opc', reader=reader, blink=blink)
