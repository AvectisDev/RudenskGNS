import requests

BASE_URL = "http://127.0.0.1:8000/api"  # local address for test
# BASE_URL = "http://10.10.12.253:8000/api"  # server address
USERNAME = "reader"
PASSWORD = "rfid-device"


def get_truck(number):
    try:
        response = requests.get(f"{BASE_URL}/trucks?registration_number={number}", auth=(USERNAME, PASSWORD))
        response.raise_for_status()
        return True, response.json()

    except requests.RequestException as e:
        return False, e.response.status_code if e.response else None


def create_truck(data):
    try:
        response = requests.post(f"{BASE_URL}/trucks", json=data, auth=(USERNAME, PASSWORD))
        response.raise_for_status()
        return True, response.json()

    except requests.RequestException as e:
        return False, e.response.status_code if e.response else None


def update_truck(number, data):
    try:
        response = requests.patch(f"{BASE_URL}/trucks", json=data, auth=(USERNAME, PASSWORD))
        response.raise_for_status()
        return True, response.json()

    except requests.RequestException as e:
        return False, e.response.status_code if e.response else None

# data = {'batch_type': 'loading', 'batch': {'batch_id': 1, 'balloons_list': ['yr5e6', '1sd', '2sd', '3sd']}}
# print(get_batch_balloons('unloading'))
# print(update_batch_balloons('loading', data))
