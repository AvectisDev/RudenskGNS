import requests
from datetime import datetime, timedelta

BASE_URL = "http://10.10.0.252:10001/lprserver/GetProtocolNumbers"  # intellect server address
USERNAME = "reader"
PASSWORD = "rfid-device"


def get_number(data):
    """
    Функция обращается к базе данных "Интеллект" и забирает номера прибывших/убывших машин и прицепов
    """
    response = requests.post(f"{BASE_URL}", json=data)

    if response.status_code == 200:
        return True, response.json()
    else:
        return False, response.status_code


def convert_time_to_string(delta_hours: int) -> str:
    start_date = datetime.now() - timedelta(hours=delta_hours)
    start_date_string = start_date.strftime("%Y-%m-%dT%H:%M:%S") + '.000'
    return start_date_string


def convert_string_to_time(time_string: str = '') -> datetime:
    date_string = datetime.strptime(time_string, "%d.%m.%Y %H:%M:%S")  # "05.08.2024 6:05:33"
    return date_string


def get_checkpoint_numbers(server_id, delta_hour):
    """
    Запрос в базе данных "Интеллект" распознанных номеров на КПП.
    Возвращает номер и дату прибывших/убывших машин и прицепов в виде списка словарей
    Для обращения к камере 25 (Весовая автотранспорта 1) "id": "2"
    Для обращения к камере 26 (Весовая автотранспорта 2) "id": "3"
    Для автовесовой нужно отправлять сразу 2 - "id": "2, 3"

    Для обращения к камере 27 (Распознавание номеров КПП Выезд) "id": "4", direction = 1 - от камеры, 2 - к камере
    Для обращения к камере 28 (Распознавание номеров КПП Въезд) "id": "5"
    """

    data_for_request = {
        "id": server_id,
        "time_from": convert_time_to_string(delta_hour),
        "numbers_operation": "OR"
    }
    get_status, data = get_number(data_for_request)

    out_list = []
    if get_status and len(data) > 0:
        
        for item in data['Protocols']:
            temp_dict = {}
            temp_dict['registration_number'] = item['number']
            date_from_camera = convert_string_to_time(item['date'])

            if server_id == '4' and item['direction'] == '1':
                temp_dict['entry_date'] = date_from_camera.date()
                temp_dict['entry_time'] = date_from_camera.time()
            if server_id == '4' and item['direction'] == '2':
                temp_dict['departure_date'] = date_from_camera.date()
                temp_dict['departure_time'] = date_from_camera.time()
            if server_id == '5' and item['direction'] == '2':
                temp_dict['entry_date'] = date_from_camera.date()
                temp_dict['entry_time'] = date_from_camera.time()
            if server_id == '5' and item['direction'] == '1':
                temp_dict['departure_date'] = date_from_camera.date()
                temp_dict['departure_time'] = date_from_camera.time()

            out_list.append(temp_dict)

    return out_list


if __name__ == "__main__":
    print(get_checkpoint_numbers('5', 8))

example = {
    'number': 'AP75311', 'detectors_name': 'Распознавание номеров КПП Въезд',
    'country': 'BLR', 'date': '02.09.2024 12:42:26', 'direction': '1', 'validity': '100', 'camera': 'Камера 28'
}

