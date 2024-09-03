import requests

TRUCKS_URL = "http://10.10.12.253:8000/api/trucks"
TRAILERS_URL = "http://10.10.12.253:8000/api/trailers"
USERNAME = "reader"
PASSWORD = "rfid-device"


def get_transport(number, transport_type):
    if transport_type == 'truck':
        BASE_URL = TRUCKS_URL
    elif transport_type == 'trailer':
        BASE_URL = TRAILERS_URL

    try:
        response = requests.get(f"{BASE_URL}?registration_number={number}", auth=(USERNAME, PASSWORD))
        response.raise_for_status()
        return True, response.json()

    except requests.RequestException as e:
        return False, e.response.status_code if e.response else None


def create_transport(data, transport_type):
    if transport_type == 'truck':
        BASE_URL = TRUCKS_URL
    elif transport_type == 'trailer':
        BASE_URL = TRAILERS_URL

    try:
        response = requests.post(BASE_URL, json=data, auth=(USERNAME, PASSWORD))
        response.raise_for_status()
        return True, response.json()

    except requests.RequestException as e:
        return False, e.response.status_code if e.response else None


def update_transport(data, transport_type):
    if transport_type == 'truck':
        BASE_URL = TRUCKS_URL
    elif transport_type == 'trailer':
        BASE_URL = TRAILERS_URL

    try:
        response = requests.patch(BASE_URL, json=data, auth=(USERNAME, PASSWORD))
        response.raise_for_status()
        return True, response.json()

    except requests.RequestException as e:
        return False, e.response.status_code if e.response else None

