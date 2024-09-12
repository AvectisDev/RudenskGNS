import aiohttp
import asyncio

BASE_URL = "http://10.10.12.253:8000/api"  # server address
TRUCKS_URL = "http://10.10.12.253:8000/api/trucks"
TRAILERS_URL = "http://10.10.12.253:8000/api/trailers"
USERNAME = "reader"
PASSWORD = "rfid-device"


async def get_transport(number, transport_type):
    if transport_type == 'truck':
        BASE_URL = TRUCKS_URL
    elif transport_type == 'trailer':
        BASE_URL = TRAILERS_URL
    else:
        return False, "Invalid transport type"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{BASE_URL}?registration_number={number}",
                                   auth=aiohttp.BasicAuth(USERNAME, PASSWORD)) as response:
                response.raise_for_status()
                return True, await response.json()

        except aiohttp.ClientError as e:
            return False, e


async def create_transport(data, transport_type):
    if transport_type == 'truck':
        BASE_URL = TRUCKS_URL
    elif transport_type == 'trailer':
        BASE_URL = TRAILERS_URL
    else:
        return False, "Invalid transport type"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(BASE_URL, json=data, auth=aiohttp.BasicAuth(USERNAME, PASSWORD)) as response:
                response.raise_for_status()  # HTTPError для ответа с кодами состояния 4xx/5xx
                return True, await response.json()

        except aiohttp.ClientError as e:
            return False, e


async def update_transport(data, transport_type):
    if transport_type == 'truck':
        BASE_URL = TRUCKS_URL
    elif transport_type == 'trailer':
        BASE_URL = TRAILERS_URL
    else:
        return False, "Invalid transport type"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.patch(BASE_URL, json=data, auth=aiohttp.BasicAuth(USERNAME, PASSWORD)) as response:
                response.raise_for_status()  # HTTPError для ответов с кодами состояния 4xx/5xx
                return True, await response.json()

        except aiohttp.ClientError as e:
            return False, e


async def get_batch_gas():
    """Проверяет наличие в базе данных активных партий отгрузки газа в автоцистернах и возвращает признак True и данные
    активной партии, если партия есть в базе, и False - если таких партий нет.

    Returns:
        tuple: (bool, str or dict) - статус наличия партии и данные партии или сообщение об ошибке.
    """
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{BASE_URL}/auto-gas-loading", timeout=1,
                                   auth=aiohttp.BasicAuth(USERNAME, PASSWORD)) as response:
                response.raise_for_status()
                data = await response.json()
                return True, data

        except aiohttp.ClientError as e:
            return False, {"status": str(e)}  # Возвращаем сообщение об ошибке запроса

        except (ValueError, KeyError):  # Обработка ошибок парсинга JSON и доступа к ключам
            return False, {"status": "invalid response"}


async def create_batch_gas(data):
    """Создает новую партию приёмки газа в автоцистернах с использованием асинхронного HTTP-запроса.

    Args:
        data (dict): Данные партии газа для создания.

    Returns:
        tuple: (bool, str or dict) - статус операции и данные созданной партии или сообщение об ошибке.
    """
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{BASE_URL}/auto-gas-loading", json=data,
                                    auth=aiohttp.BasicAuth(USERNAME, PASSWORD)) as response:
                response.raise_for_status()
                return True, await response.json()

        except aiohttp.ClientError as e:
            return False, {"status": str(e)}

        except (ValueError, KeyError):  # Обработка ошибок парсинга JSON и доступа к ключам
            return False, {"status": "invalid response"}


async def update_batch_gas(data):
    """
    Обновляет партию приёмки газа в автоцистернах с использованием асинхронного HTTP-запроса.

    Args:
        data (dict): Данные партии газа для обновления.

    Returns:
        tuple: (bool, dict) - статус операции и сообщение о результатах обновления.
    """
    async with aiohttp.ClientSession() as session:
        try:
            async with session.patch(f"{BASE_URL}/auto-gas-loading", json=data,
                                     auth=aiohttp.BasicAuth(USERNAME, PASSWORD)) as response:
                response.raise_for_status()  # Поднимает исключение для 4xx и 5xx
                return True, {"status": "ok"}

        except KeyError:
            return False, {"status": "no valid response - missing key"}
