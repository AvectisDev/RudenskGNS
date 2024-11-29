import aiohttp
import asyncio

BASE_URL = "http://10.10.12.253:8000/api"  # server address
USERNAME = "reader"
PASSWORD = "rfid-device"


# async def get_balloon(nfc_tag):
#     async with aiohttp.ClientSession() as session:
#         try:
#             async with session.get(f"{BASE_URL}/balloons/nfc/{nfc_tag}/", timeout=3,
#                                    auth=aiohttp.BasicAuth(USERNAME, PASSWORD)) as response:
#
#                 response.raise_for_status()  # Поднимает исключение для 4xx и 5xx
#                 return await response.json()
#
#         except (aiohttp.ClientError, asyncio.TimeoutError) as error:
#             print(f'get_balloon function error: {error}')
#             return None
#
#
# async def create_balloon(data):
#     async with aiohttp.ClientSession() as session:
#         try:
#             async with session.post(f"{BASE_URL}/balloons/", json=data, timeout=3,
#                                     auth=aiohttp.BasicAuth(USERNAME, PASSWORD)) as response:
#                 response.raise_for_status()
#                 return await response.json()
#
#         except (aiohttp.ClientError, asyncio.TimeoutError) as error:
#             print(f'create_balloon function error: {error}')
#             return None


async def update_balloon(data):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{BASE_URL}/balloons/update-by-reader/", json=data, timeout=3,
                                     auth=aiohttp.BasicAuth(USERNAME, PASSWORD)) as response:
                response.raise_for_status()
                return await response.json()

        except (aiohttp.ClientError, asyncio.TimeoutError) as error:
            print(f'update_balloon function error: {error}')
            return None


async def update_balloon_amount(from_who: str, data):
    if from_who == 'rfid':
        url = f'{BASE_URL}/balloons-amount/update-amount-of-rfid/'
    elif from_who == 'sensor':
        url = f'{BASE_URL}/balloons-amount/update-amount-of-sensor/'
    else:
        return None

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=data, timeout=3,
                                     auth=aiohttp.BasicAuth(USERNAME, PASSWORD)) as response:
                response.raise_for_status()
                return await response.json()

        except (aiohttp.ClientError, asyncio.TimeoutError) as error:
            print(f'update_balloon_amount function error: {error}')
            return None


async def get_batch_balloons(batch_type: str):
    """Проверяет наличие в базе данных активных партий и возвращает признак True и данные активной партии, если
    партия есть в базе, и False - если таких партий нет.

    Args:
        batch_type (str): Тип партии для запроса.

    Returns:
        dict: (dict) - данные партии или None.
    """

    if batch_type == 'loading':
        url = f'{BASE_URL}/balloons-loading/last-active/'
    elif batch_type == 'unloading':
        url = f'{BASE_URL}/balloons-unloading/last-active/'
    else:
        print(f'get_batch_balloons function error: No batch type')
        return None

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=3, auth=aiohttp.BasicAuth(USERNAME, PASSWORD)) as response:
                response.raise_for_status()
                return await response.json()

        except (aiohttp.ClientError, asyncio.TimeoutError) as error:
            print(f'get_batch_balloons function error: {error}')
            return None
        except ValueError as error:  # Обработка ошибок кода JSON
            print(f'get_batch_balloons function error: {error}')
            return None


async def add_balloon_to_batch(reader: dict):
    batch_type = reader['function']

    batch_id = reader['batch']['batch_id']

    if batch_type == 'loading':
        url = f'{BASE_URL}/balloons-loading/{batch_id}/add-balloon/'
    elif batch_type == 'unloading':
        url = f'{BASE_URL}/balloons-unloading/{batch_id}/add-balloon/'
    else:
        print(f'get_batch_balloons function error: No batch type')
        return None

    data = {
        'balloon_id': reader['batch']['balloon_id']
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.patch(url, json=data, timeout=3, auth=aiohttp.BasicAuth(USERNAME, PASSWORD)) as response:
                response.raise_for_status()
                return response.status

        except (aiohttp.ClientError, asyncio.TimeoutError) as error:
            print(f'update_batch_balloons function error: {error}')
            return None
        except ValueError as error:  # Обработка ошибок кода JSON
            print(f'update_batch_balloons function error: {error}')
            return None
        except KeyError as error:
            print(f'update_batch_balloons function error: {error}')
            return None
