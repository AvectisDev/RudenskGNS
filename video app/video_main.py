import requests
from datetime import datetime, timedelta

BASE_URL = "http://10.10.0.252:10001/lprserver/GetProtocolNumbers"  # intellect server address
USERNAME = "reader"
PASSWORD = "rfid-device"


def get_number(data):
    response = requests.post(f"{BASE_URL}", json=data)

    if response.status_code == 200:
        return True, response.json()
    else:
        return False, response.status_code


if __name__ == "__main__":
    print(datetime.now())
    data_for_request = {
        "id": "5",
        "time_from": datetime.now() - timedelta(hours=8),
        "numbers_operation": "OR"
    }
    get_number(data_for_request)
