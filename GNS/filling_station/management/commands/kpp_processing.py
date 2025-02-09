import logging
from django.core.cache import cache
from opcua import Client, ua
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.management.base import BaseCommand
from datetime import datetime
from filling_station.models import RailwayBatch, RailwayTank
from .intellect import get_registration_number_list, INTELLECT_SERVER_LIST

logger = logging.getLogger('filling_station')


class Command(BaseCommand):
    def __init__(self):
        super().__init__()
        self.client = Client("opc.tcp://host.docker.internal:4841")
        self.last_number = cache.get('last_tank_number', '')

    def get_opc_value(self, addr_str):
        """Получить значение с OPC UA сервера по адресу."""
        var = self.client.get_node(addr_str)
        return var.get_value()

    def set_opc_value(self, addr_str, value):
        """Установить значение на OPC UA сервере по адресу."""
        var = self.client.get_node(addr_str)
        return var.set_attribute(ua.AttributeIds.Value, ua.DataValue(value))

    def handle(self, *args, **kwargs):
        try:
            self.client.connect()
            logger.info('Connect to OPC server successful')

            tank_weight = self.get_opc_value("ns=4; s=Address Space.PLC_SU1.tank.stable_weight")
            camera_worked = self.get_opc_value("ns=4; s=Address Space.PLC_SU1.tank.camera_worked")
            is_on_station = self.get_opc_value("ns=4; s=Address Space.PLC_SU1.tank.on_station")

            logger.info(f'tank_weight={tank_weight}, camera_worked={camera_worked}, is_on_station={is_on_station}')

            if camera_worked:
                logger.info(f'Камера сработала. Вес жд цистерны {tank_weight}')
                current_date = datetime.now().date()
                current_time = datetime.now().time()

                # получаем от "Интеллекта" список номеров с данными фотофиксации
                railway_tank_list = get_registration_number_list(INTELLECT_SERVER_LIST[0])

                if not railway_tank_list:
                    logger.info('ЖД цистерна не определена')
                    return

                # работаем с номером последней цистерны
                railway_tank = railway_tank_list[-1]
                registration_number = railway_tank['registration_number']

                if registration_number != self.last_number:
                    cache.set('last_tank_number', self.last_number)
                try:
                    railway_tank, tank_created = RailwayTank.objects.get_or_create(
                        registration_number=registration_number,
                        defaults={
                            'registration_number': registration_number,
                            'is_on_station': is_on_station,
                            'entry_date': current_date if is_on_station else None,
                            'entry_time': current_time if is_on_station else None,
                            'departure_date': current_date if not is_on_station else None,
                            'departure_time': current_time if not is_on_station else None,
                            'full_weight': tank_weight if is_on_station else None,
                            'empty_weight': tank_weight if not is_on_station else None,
                        }
                    )
                    if not tank_created:
                        railway_tank.is_on_station = is_on_station
                        if is_on_station:
                            railway_tank.entry_date = current_date
                            railway_tank.entry_time = current_time
                            railway_tank.departure_date = None
                            railway_tank.departure_time = None
                            railway_tank.full_weight = tank_weight
                        else:
                            railway_tank.departure_date = current_date
                            railway_tank.departure_time = current_time
                            railway_tank.empty_weight = tank_weight
                            railway_tank.gas_weight = railway_tank.full_weight or 0 - tank_weight
                        railway_tank.save()
                    self.set_opc_value("ns=4; s=Address Space.PLC_SU1.tank.camera_worked", False)
                    logger.info(f'ЖД весовая. Обработка завершена. Цистерна № {registration_number}')

                except ObjectDoesNotExist:
                    logger.error(f"Объект с номером {registration_number} не существует")
                except MultipleObjectsReturned:
                    logger.error(f"Найдено более одного объекта с номером {registration_number}")
        except Exception as error:
            logger.error(f'No connection to OPC server: {error}')
            return {'error': f'No connection to OPC server: {error}'}
        finally:
            self.client.disconnect()
            logger.info('Disconnect from OPC server')
