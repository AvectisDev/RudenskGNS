# if reader['function'] is not None:  # если производится приёмка/отгрузка баллонов
#     batch_data = await balloon_api.get_batch_balloons(reader['function'])
#
#     if batch_data:  # если партия активна - добавляем в неё пройденный баллон
#         reader['batch']['batch_id'] = batch_data['id']
#         reader['batch']['balloon_id'] = balloon_passport['id']
#         await balloon_api.add_balloon_to_batch(reader)

import time
import db
import aiohttp
import asyncio
from settings import READER_LIST, COMMANDS
import balloon_api


def timing_decorator(func):
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        await func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Function '{func.__name__}' executed in {elapsed_time:.4f} seconds")
    return wrapper
#
#
# async def main():
#     @timing_decorator
#     async def decorated_write_balloons_amount(reader, sensor):
#         await db.write_balloons_amount(reader, sensor)
#
#     await decorated_write_balloons_amount(READER_LIST[0], 'sensor')


BASE_URL = "http://localhost:8000/api"  # server address
USERNAME = "admin"
PASSWORD = ".Avectis1"


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
    print(f'from who is {from_who}')
    async with aiohttp.ClientSession() as session:
        try:
            print("in function")
            async with session.post(url, json=data, timeout=3,
                                    auth=aiohttp.BasicAuth(USERNAME, PASSWORD)) as response:
                print(response)
                response.raise_for_status()

        except (aiohttp.ClientError, asyncio.TimeoutError) as error:
            print(f'update_balloon_amount function error: {error}')
            return None


async def main():
    @timing_decorator
    async def read_input_status(reader: dict):
        print("this is read_input_status function")
        data_for_amount = {
            'reader_id': reader['number'],
            'reader_status': reader['status']
        }
        print(data_for_amount)
        await balloon_api.update_balloon_amount('sensor', data_for_amount)

    print("this is main function")
    await read_input_status(READER_LIST[0])

if __name__ == "__main__":
    asyncio.run(main())
