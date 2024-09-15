import aiohttp
import asyncio

BASE_URL = "http://10.10.12.253:8000/api"  # server address
TRUCKS_URL = "http://10.10.12.253:8000/api/trucks"
TRAILERS_URL = "http://10.10.12.253:8000/api/trailers"
USERNAME = "reader"
PASSWORD = "rfid-device"


async def get_transport_path(transport_type: str):
    if transport_type == 'truck':
        return 'trucks'
    elif transport_type == 'trailer':
        return 'trailers'
    else:
        return False, "Invalid transport type"


async def get_transport(number, transport_type):
    """Проверяет наличие в базе данных транспорт по указанному регистрационному номеру и возвращает признак True и
    данные транспорта, если он есть в базе, и False - если его нет.

    Args:
        number (str): регистрационный номер транспорта
        transport_type (str): тип обрабатываемой партии

    Returns:
        tuple: (bool, str or dict) - статус наличия транспорта в базе и его данные или сообщение об ошибке.
    """
    path = await get_transport_path(transport_type)

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{BASE_URL}/{path}?registration_number={number}", timeout=5,
                                   auth=aiohttp.BasicAuth(USERNAME, PASSWORD)) as response:
                response.raise_for_status()
                return True, await response.json()

        except (aiohttp.ClientError, asyncio.TimeoutError) as error:
            return False, error  # Возвращаем сообщение об ошибке запроса

        except (ValueError, KeyError):  # Обработка ошибок парсинга JSON и доступа к ключам
            return False, {"status": "invalid response"}


async def create_transport(data, transport_type):
    path = await get_transport_path(transport_type)

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{BASE_URL}/{path}", json=data, timeout=5,
                                    auth=aiohttp.BasicAuth(USERNAME, PASSWORD)) as response:
                response.raise_for_status()  # HTTPError для ответа с кодами состояния 4xx/5xx
                return True, await response.json()

        except (aiohttp.ClientError, asyncio.TimeoutError) as error:
            return False, error  # Возвращаем сообщение об ошибке запроса

        except (ValueError, KeyError):  # Обработка ошибок парсинга JSON и доступа к ключам
            return False, {"status": "invalid response"}


async def update_transport(data, transport_type):
    path = await get_transport_path(transport_type)

    async with aiohttp.ClientSession() as session:
        try:
            async with session.patch(f"{BASE_URL}/{path}", json=data, timeout=5,
                                     auth=aiohttp.BasicAuth(USERNAME, PASSWORD)) as response:
                response.raise_for_status()  # HTTPError для ответов с кодами состояния 4xx/5xx
                return True, await response.json()

        except (aiohttp.ClientError, asyncio.TimeoutError) as error:
            return False, error  # Возвращаем сообщение об ошибке запроса

        except (ValueError, KeyError):  # Обработка ошибок парсинга JSON и доступа к ключам
            return False, {"status": "invalid response"}


async def get_batch_path(batch_type: str):
    if batch_type == 'loading':
        return 'auto-gas-loading'
    elif batch_type == 'unloading':
        return 'auto-gas-unloading'
    else:
        return False, "Invalid batch type"


async def get_batch_gas(batch_type: str):
    """Проверяет наличие в базе данных активных партий отгрузки газа в автоцистернах и возвращает признак True и данные
    активной партии, если партия есть в базе, и False - если таких партий нет.

    Args:
        batch_type (str): тип обрабатываемой партии

    Returns:
        tuple: (bool, str or dict) - статус наличия партии и данные партии или сообщение об ошибке.
    """
    path = await get_batch_path(batch_type)

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{BASE_URL}/{path}", timeout=5,
                                   auth=aiohttp.BasicAuth(USERNAME, PASSWORD)) as response:
                response.raise_for_status()
                data = await response.json()
                return True, data

        except (aiohttp.ClientError, asyncio.TimeoutError) as error:
            return False, error  # Возвращаем сообщение об ошибке запроса

        except (ValueError, KeyError):  # Обработка ошибок парсинга JSON и доступа к ключам
            return False, {"status": "invalid response"}


async def create_batch_gas(data, batch_type: str):
    """Создает новую партию приёмки/отгрузки газа в автоцистернах с использованием асинхронного HTTP-запроса.

    Args:
        data (dict): данные партии газа для создания
        batch_type (str): тип обрабатываемой партии

    Returns:
        tuple: (bool, str or dict) - статус операции и данные созданной партии или сообщение об ошибке.
    """
    path = await get_batch_path(batch_type)

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{BASE_URL}/{path}", json=data, timeout=5,
                                    auth=aiohttp.BasicAuth(USERNAME, PASSWORD)) as response:
                response.raise_for_status()
                return True, await response.json()

        except (aiohttp.ClientError, asyncio.TimeoutError) as error:
            return False, error  # Возвращаем сообщение об ошибке запроса

        except (ValueError, KeyError):  # Обработка ошибок парсинга JSON и доступа к ключам
            return False, {"status": "invalid response"}


async def update_batch_gas(data, batch_type: str):
    """
    Обновляет партию приёмки/отгрузки газа в автоцистернах с использованием асинхронного HTTP-запроса.

    Args:
        data (dict): данные партии газа для обновления
        batch_type (str): тип обрабатываемой партии

    Returns:
        tuple: (bool, dict) - статус операции и сообщение о результатах обновления.
    """
    path = await get_batch_path(batch_type)

    async with aiohttp.ClientSession() as session:
        try:
            async with session.patch(f"{BASE_URL}/{path}", json=data, timeout=5,
                                     auth=aiohttp.BasicAuth(USERNAME, PASSWORD)) as response:
                response.raise_for_status()  # Поднимает исключение для 4xx и 5xx
                return True, {"status": "ok"}

        except (aiohttp.ClientError, asyncio.TimeoutError) as error:
            return False, error  # Возвращаем сообщение об ошибке запроса

        except (ValueError, KeyError):  # Обработка ошибок парсинга JSON и доступа к ключам
            return False, {"status": "invalid response"}
