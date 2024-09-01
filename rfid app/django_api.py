import requests

BASE_URL = "http://127.0.0.1:8000/api"  # local address for test
# BASE_URL = "http://10.10.12.253:8000/api"  # server address
USERNAME = "reader"
PASSWORD = "rfid-device"


def get_balloon(nfc_tag):
    response = requests.get(f"{BASE_URL}/BalloonPassport?nfc_tag={nfc_tag}", auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        return True, response.json()
    else:
        return False, response.status_code


def create_balloon(data):
    response = requests.post(f"{BASE_URL}/BalloonPassport", json=data, auth=(USERNAME, PASSWORD))

    if response.status_code == 201:
        return True, response.json()
    else:
        return False, response.status_code


def update_balloon(nfc_tag, data):
    response = requests.patch(f"{BASE_URL}/BalloonPassport?nfc_tag={nfc_tag}", json=data, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        return True, response.json()
    else:
        return False, response.status_code


def get_batch_balloons(batch_type: str):
    """Проверяет наличие в базе данных активных партий и возвращает признак True и данные активной партии, если
    партия есть в базе, и False - если таких партий нет.

    Args:
        batch_type (str): Тип партии для запроса.

    Returns:
        tuple: (bool, str or dict) - статус наличия партии и номер партии или сообщение об ошибке.
    """

    if batch_type == 'loading':
        url = f'{BASE_URL}/BalloonsLoading'
    elif batch_type == 'unloading':
        url = f'{BASE_URL}/BalloonsUnloading'
    else:
        url = f' '

    try:
        response = requests.get(url, timeout=1, auth=(USERNAME, PASSWORD))
        response.raise_for_status()  # Проверка на успешный статус-код
    except requests.exceptions.RequestException as e:
        return False, {"status": str(e)}  # Вернет сообщение об ошибке запроса

    try:
        data = response.json()
        if response.status_code == 200:
            print(data)
            return True, data

        return False, data.get('error', "Unknown error")
    except (ValueError, KeyError):  # Обработка ошибок кода JSON и ключей
        return False, {"status": "invalid response"}


def update_batch_balloons(batch_type, reader: dict):
    url = f'{BASE_URL}/UpdateBatchBalloons'
    data = {
        'batch_type': batch_type,
        'batch_id': reader['batch']['batch_id'],
        'balloons_list': reader['batch']['balloons_list']
    }

    try:
        response = requests.post(url, json=data, timeout=1)
        response.raise_for_status()  # Поднимает исключение для 4xx и 5xx
        return True, {"status": "ok"}
    except KeyError:
        return False, {"status": "no valid response - missing key"}
    except requests.RequestException as e:  # Уточняем исключения requests
        return False, {"status": f"request failed: {str(e)}"}


# data = {'batch_type': 'loading', 'batch': {'batch_id': 1, 'balloons_list': ['yr5e6', '1sd', '2sd', '3sd']}}
print(get_batch_balloons('unloading'))
# print(update_batch_balloons('loading', data))
