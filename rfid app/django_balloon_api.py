import aiohttp
import asyncio

# BASE_URL = "http://127.0.0.1:8000/api"  # local address for test
BASE_URL = "http://10.10.12.253:8000/api"  # server address
USERNAME = "reader"
PASSWORD = "rfid-device"


async def get_balloon(nfc_tag):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{BASE_URL}/balloon-passport?nfc_tag={nfc_tag}", timeout=2,
                                   auth=aiohttp.BasicAuth(USERNAME, PASSWORD)) as response:

                response.raise_for_status()  # Поднимает исключение для 4xx и 5xx
                return True, await response.json()

        except aiohttp.ClientError as e:
            return False, response.status if response else None


async def create_balloon(data):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{BASE_URL}/balloon-passport", json=data, timeout=2,
                                    auth=aiohttp.BasicAuth(USERNAME, PASSWORD)) as response:
                response.raise_for_status()  # Поднимает исключение для 4xx и 5xx
                return True, await response.json()

        except aiohttp.ClientError as e:
            return False, response.status if response else None


async def update_balloon(nfc_tag, data):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.patch(f"{BASE_URL}/balloon-passport?nfc_tag={nfc_tag}", json=data, timeout=2,
                                     auth=aiohttp.BasicAuth(USERNAME, PASSWORD)) as response:
                response.raise_for_status()  # вызывает исключение для кодов ошибок HTTP
                return True, await response.json()

        except aiohttp.ClientError as e:
            return False, response.status if response else None


async def get_batch_balloons(batch_type: str):
    """Проверяет наличие в базе данных активных партий и возвращает признак True и данные активной партии, если
    партия есть в базе, и False - если таких партий нет.

    Args:
        batch_type (str): Тип партии для запроса.

    Returns:
        tuple: (bool, str or dict) - статус наличия партии и данные партии или сообщение об ошибке.
    """

    if batch_type == 'loading':
        url = f'{BASE_URL}/balloons-loading'
    elif batch_type == 'unloading':
        url = f'{BASE_URL}/balloons-unloading'
    else:
        return False, {"status": "invalid batch_type"}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=2, auth=aiohttp.BasicAuth(USERNAME, PASSWORD)) as response:
                response.raise_for_status()  # Проверка на успешный статус-код
                data = await response.json()

                if response.status == 200:
                    return True, data

                return False, {'error': "Unknown error"}
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            return False, {"status": str(e)}
        except ValueError:  # Обработка ошибок кода JSON
            return False, {"status": "invalid response"}


async def update_batch_balloons(batch_type: str, reader: dict):
    if batch_type == 'loading':
        url = f'{BASE_URL}/balloons-loading'
    elif batch_type == 'unloading':
        url = f'{BASE_URL}/balloons-unloading'
    else:
        return False, {"status": "invalid batch_type"}

    data = {
        'id': reader['batch']['batch_id'],
        'balloon_list': reader['batch']['balloon_list']
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.patch(url, json=data, timeout=2, auth=aiohttp.BasicAuth(USERNAME, PASSWORD)) as response:
                response.raise_for_status()  # Поднимает исключение для 4xx и 5xx
                return True, {"status": "ok"}
        except KeyError:
            return False, {"status": "no valid response - missing key"}
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            return False, {"status": str(e)}
