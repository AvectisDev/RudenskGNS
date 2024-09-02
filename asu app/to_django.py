import requests

BASE_URL = "http://127.0.0.1:8000/api"  # local address for test
# BASE_URL = "http://10.10.12.253:8000/api"  # server address
USERNAME = "reader"
PASSWORD = "rfid-device"


def get_truck(number):
    response = requests.get(f"{BASE_URL}/trucks?registration_number={number}", auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        return True, response.json()
    else:
        return False, response.status_code


def create_truck(data):
    response = requests.post(f"{BASE_URL}/trucks", json=data, auth=(USERNAME, PASSWORD))

    if response.status_code == 201:
        return True, response.json()
    else:
        return False, response.status_code


def update_truck(number, data):
    response = requests.patch(f"{BASE_URL}/trucks", json=data, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        return True, response.json()
    else:
        return False, response.status_code

# data = {'batch_type': 'loading', 'batch': {'batch_id': 1, 'balloons_list': ['yr5e6', '1sd', '2sd', '3sd']}}
# print(get_batch_balloons('unloading'))
# print(update_batch_balloons('loading', data))
