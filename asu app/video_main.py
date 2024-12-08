import asyncio
from datetime import datetime, timedelta
import video_api
import logging
from opcua import Client, ua
from settings import INTELLECT_SERVER_LIST, AUTO, RAILWAY
from intellect_functions import (separation_string_date, get_registration_number_list, check_on_station,
                                 get_transport_type)

logging.basicConfig(
    level=logging.INFO,  # Уровень логирования
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='video_app_logs.log',
    filemode='w',
    encoding='utf-8'
)

logger = logging.getLogger('app_logger')
logger.setLevel(logging.DEBUG)


def get_opc_value(addr_str):
    """
    Get value from OPC UA server by address:
    Can look it in Editor.exe(SimpleScada)->Variable-> Double-click on the necessary variable->address
    """
    var = client.get_node(addr_str)
    return var.get_value()


def set_opc_value(addr_str, value):
    """
    Get value from OPC UA server by address:
    Can look it in Editor.exe(SimpleScada)->Variable-> Double-click on the necessary variable->address
    """
    var = client.get_node(addr_str)
    return var.set_attribute(ua.AttributeIds.Value, ua.DataValue(value))


def get_opc_data():

    try:
        client.connect()
        logger.debug('Connect to OPC server successful')

        if AUTO['response_number_detect']:
            set_opc_value("ns=4; s=Address Space.PLC_SU2.Batches.response_number_detect", True)
        if AUTO['response_batch_complete']:
            set_opc_value("ns=4; s=Address Space.PLC_SU2.Batches.response_batch_complete", True)

        RAILWAY['tank_weight'] = get_opc_value("ns=4; s=Address Space.PLC_SU1.railway_tank_weight")
        RAILWAY['weight_is_stable'] = get_opc_value("ns=4; s=Address Space.PLC_SU1.railway_tank_weight_is_stable")
        RAILWAY['camera_worked'] = get_opc_value("ns=4; s=Address Space.PLC_SU1.camera_worked")

        AUTO['batch_type'] = get_opc_value("ns=4; s=Address Space.PLC_SU2.Batches.batch_type")
        AUTO['gas_type'] = get_opc_value("ns=4; s=Address Space.PLC_SU2.Batches.gas_type")

        AUTO['initial_mass_meter'] = get_opc_value("ns=4; s=Address Space.PLC_SU2.Batches.initial_mass_meter")
        AUTO['final_mass_meter'] = get_opc_value("ns=4; s=Address Space.PLC_SU2.Batches.final_mass_meter")
        AUTO['gas_amount'] = get_opc_value("ns=4; s=Address Space.PLC_SU2.Batches.gas_amount")

        AUTO['truck_full_weight'] = get_opc_value("ns=4; s=Address Space.PLC_SU2.Batches.truck_full_weight")
        AUTO['truck_empty_weight'] = get_opc_value("ns=4; s=Address Space.PLC_SU2.Batches.truck_empty_weight")
        AUTO['weight_gas_amount'] = get_opc_value("ns=4; s=Address Space.PLC_SU2.Batches.weight_gas_amount")

        AUTO['request_number_identification'] = get_opc_value("ns=4; s=Address Space.PLC_SU2.Batches.request_number_identification")
        AUTO['request_batch_complete'] = get_opc_value("ns=4; s=Address Space.PLC_SU2.Batches.request_batch_complete")

        logger.debug(f'Auto:{AUTO}, Railway:{RAILWAY}')

    except Exception as error:
        logger.error(f'No connection to OPC server: {error}')
    finally:
        client.disconnect()
        logger.debug('Disconnect from OPC server')


async def transport_process(transport: dict):
    registration_number = transport['registration_number']
    date, time = separation_string_date(transport['date'])
    is_on_station = check_on_station(transport)

    transport_type = get_transport_type(registration_number)

    if transport_type:
        # проверяем наличие в базе данных транспорт с данным номером
        transport_data = await video_api.get_transport(registration_number, transport_type)

        if transport_data:
            transport_data['is_on_station'] = is_on_station
            if is_on_station:
                transport_data['entry_date'] = date
                transport_data['entry_time'] = time
                transport_data['departure_date'] = None
                transport_data['departure_time'] = None
            else:
                transport_data['departure_date'] = date
                transport_data['departure_time'] = time

            result = await video_api.update_transport(transport_data, transport_type)
            logger.debug(f'{transport_type} with number {transport['registration_number']} update')

        else:
            entry_date = entry_time = departure_date = departure_time = None
            if is_on_station:
                entry_date, entry_time = date, time
            else:
                departure_date, departure_time = date, time

            new_transport_data = {
                'registration_number': registration_number,
                'entry_date': entry_date,
                'entry_time': entry_time,
                'departure_date': departure_date,
                'departure_time': departure_time,
                'is_on_station': is_on_station
            }
            # result = await video_api.create_transport(new_transport_data, transport_type)
            # logger.debug(f'{transport_type} with number {transport['registration_number']} create')
        return result
    else:
        return None


async def auto_batch_processing(server):
    """
    Формирование и обработка партий приёмки/отгрузки газа в автоцистернах
    """

    if AUTO['request_number_identification']:  # Поиск машины в базе. Создание партии
        logger.debug('Автовесовая. Запрос определения номера. Начало партии приёмки')

        transport_list = await get_registration_number_list(server)
        logger.debug(f'Автовесовая. Список номеров: {transport_list}')

        if not transport_list:
            logger.debug('Автоколонка. Машина не определена')
            return

        for transport in reversed(transport_list):  # начинаем с последней определённой машины
            registration_number = transport['registration_number']
            transport_type = get_transport_type(registration_number)

            if transport_type == 'truck' and not AUTO['truck_id']:
                logger.debug(f'Автоколонка. Машина на весах. Номер - {registration_number}')

                # запрос данных по текущему номеру машины
                truck_data = await video_api.get_transport(registration_number, transport_type)
                if truck_data:
                    AUTO['truck_id'] = truck_data['id']

            if transport_type == 'trailer' and not AUTO['trailer_id']:
                logger.debug(f'Автоколонка. Прицеп на весах. Номер - {registration_number}')

                # запрос данных по текущему номеру прицепа
                trailer_data = await video_api.get_transport(registration_number, transport_type)
                if trailer_data:
                    AUTO['trailer_id'] = trailer_data['id']

        if AUTO['gas_type'] == 2:
            gas_type = 'СПБТ'
        elif AUTO['gas_type'] == 3:
            gas_type = 'ПБА'
        else:
            gas_type = 'Не выбран'

        batch_data = {
            'batch_type': 'l' if AUTO['batch_type'] == 'loading' else 'u',
            'truck': AUTO['truck_id'],
            'trailer': 0 if not AUTO['trailer_id'] else AUTO['trailer_id'],
            'is_active': True,
            'gas_type': gas_type
        }

        # начинаем партию
        logger.debug(f'Автоколонка. Запрос создания партии. Данные - {batch_data}')
        batch_data = await video_api.create_batch_gas(batch_data)
        AUTO['batch_id'] = batch_data['id']
        AUTO['response_number_detect'] = True

    if AUTO['request_batch_complete']:
        batch_data = {
            'is_active': False,
            'initial_mass_meter': AUTO['initial_mass_meter'],
            'final_mass_meter': AUTO['final_mass_meter'],
            'gas_amount': AUTO['gas_amount'],
            'truck_full_weight': AUTO['truck_full_weight'],
            'truck_empty_weight': AUTO['truck_empty_weight'],
            'weight_gas_amount': AUTO['weight_gas_amount'],
        }
        # завершаем партию приёмки газа
        logger.debug(f'Автоколонка. Запрос редактирования партии. Данные - {batch_data}')
        await video_api.update_batch_gas(AUTO['batch_id'], batch_data)
        AUTO['response_batch_complete'] = True


async def kpp_processing(server: dict):
    logger.debug('Обработка регистрационных номеров на КПП')

    # получаем от "Интеллекта" список номеров с данными фотофиксации
    transport_list = await get_registration_number_list(server)

    # Задачи для обработки регистрационных номеров на КПП
    for transport in transport_list:
        await transport_process(transport)


async def railway_processing(server: dict):
    logger.debug('Обработка жд цистерн')

    if RAILWAY['camera_worked']:
        weight = RAILWAY['tank_weight']

        # получаем от "Интеллекта" список номеров с данными фотофиксации
        railway_tank_list = await get_registration_number_list(server)
        if not railway_tank_list:
            logger.debug('ЖД весовая. Цистерна не определена')
            return

        # работаем с номером последней цистерны
        railway_tank_data = railway_tank_list[-1]
        if railway_tank_data['registration_number'] != RAILWAY['last_number']:
            RAILWAY['last_number'] = railway_tank_data['registration_number']
            railway_tank = await transport_process(railway_tank_data)

            if railway_tank['is_on_station']:
                railway_tank['full_weight'] = weight
            else:
                railway_tank['gas_weight'] = railway_tank['full_weight'] - weight
                railway_tank['empty_weight'] = weight

            await video_api.update_transport(railway_tank, 'railway_tank')
            logger.debug(f'ЖД весовая. Цистерна № {RAILWAY['last_number']} на весах. Вес = {weight} тонн')


async def periodic_kpp_processing():
    while True:
        # Задачи обработки номеров на КПП. Сервера 4 и 5
        await kpp_processing(INTELLECT_SERVER_LIST[2])
        await asyncio.sleep(60)  # 60 секунд = 1 минута


async def periodic_railway_processing():
    while True:
        # Задачи обработки жд цистерн. Сервер 1
        await railway_processing(INTELLECT_SERVER_LIST[0])
        await asyncio.sleep(2)


async def main():
    kpp_task = asyncio.create_task(periodic_kpp_processing())
    railway_task = asyncio.create_task(periodic_railway_processing())

    while True:
        # Обработка данных OPC сервера
        get_opc_data()

        # Обработка процессов приёмки/отгрузки газа в автоцистернах
        await auto_batch_processing(INTELLECT_SERVER_LIST[1])
        await asyncio.sleep(2)


if __name__ == "__main__":
    client = Client("opc.tcp://127.0.0.1:4841")
    # client = Client("opc.tcp://host.docker.internal:4841") # for work with docker
    asyncio.run(main())
