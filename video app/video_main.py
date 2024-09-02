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
    date = datetime.now() - timedelta(hours=4)
    date_string = date.strftime("%Y-%m-%dT%H:%M:%S") + '.000'
    data_for_request = {
        "id": "5",
        "time_from": date_string,
        "numbers_operation": "OR"
    }
    get_status, data = get_number(data_for_request)

    if get_status:
        for item in data['Protocols']:
            print(item)

{'plate_numbers.id': '{0CF2FDD8-2869-EF11-837C-3CECEFF59ECD}', 'frame': '', 'license_plate': '', 'regional_code': '', 'number': 'AP75311', 'detectors_name': 'Распознавание номеров КПП Въезд', 
 'speed': '', 'country': 'BLR', 'date': '02.09.2024 12:42:26', 'recognizer_address': '', 'valid_speed': '', 'speeding': '', 'direction': '1', 'validity': '100', 'alarm time': '', 
 'alarm_initiated_by': '', 'alarm_accepted_by': '', 'comment_from_external_db': '', 'alarm_accepted_at': '', 'alarm_handling_delay': '', 'comment': '', 'alarm_type': '', 'alarm_processed': '', 
 'external_db': '', 'red_light_phase_start_time': '', 'time_passed_since_the_red_light_phase_start': '', 'category': '', 'camera': 'Камера 28', 'type': '', 'vendor': '', 'model': '', 
 'frame_from_synchronous_camera': '', 'dangerous_goods_class': '', 'dangerous_goods_composition': ''}