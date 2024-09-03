import requests
import schedule
from datetime import datetime, timedelta
import to_django

BASE_URL = "http://10.10.0.252:10001/lprserver/GetProtocolNumbers"  # intellect server address
USERNAME = "reader"
PASSWORD = "rfid-device"
START_TIME = 1  # данные запрашиваются начиная с времени = текущее время - указанное количество часов


def get_number(data):
    """
    Функция обращается к базе данных "Интеллект" и забирает номера прибывших/убывших машин и прицепов
    data: словарь с данными для запроса
    return: кортеж -
             True и JSON-ответ при успешном запросе;
             False и код статуса при ошибке
    """
    try:
        response = requests.post(BASE_URL, json=data)

        response.raise_for_status()  # Вызывает исключение для ошибок HTTP (коды статусов 4xx и 5xx)

        return True, response.json()

    except requests.RequestException as e:
        return False, e.response.status_code if e.response else None


def get_time_from(delta_hours: int) -> str:
    start_date = datetime.now() - timedelta(hours=delta_hours)
    start_date_string = f'{start_date.strftime("%Y-%m-%dT%H:%M:%S")}.000'
    return start_date_string


def convert_string_to_time(time_string: str = '') -> datetime:
    try:
        converted_time = datetime.strptime(time_string, "%d.%m.%Y %H:%M:%S")
    except ValueError as e:
        raise ValueError(f"Invalid date format: {str(e)}")
    return converted_time


def convert_time_to_string(data_object) -> tuple:
    string_date = data_object.strftime("%Y-%m-%d")
    string_time = data_object.strftime("%H:%M")
    return string_date, string_time


def get_checkpoint_numbers(server_id, delta_hour) -> list:
    """
    Запрос в базе данных "Интеллект" распознанных номеров на КПП.
    Возвращает номер и дату прибывших/убывших машин и прицепов в виде списка словарей.
    Используйте следующие идентификаторы камер:
    - Камера 25 (Весовая автотранспорта 1) -> "id": "2"
    - Камера 26 (Весовая автотранспорта 2) -> "id": "3"
    Для автовесовой нужно отправлять сразу 2 - "id": "2, 3"

    - Камера 27 (Распознавание номеров КПП Выезд) -> "id": "4", direction = 1 - от камеры, 2 - к камере
    - Камера 28 (Распознавание номеров КПП Въезд) -> "id": "5", direction = 1 - от камеры, 2 - к камере
    """

    data_for_request = {
        "id": server_id,
        "time_from": get_time_from(delta_hour),
        "numbers_operation": "OR"
    }
    get_status, data = get_number(data_for_request)

    out_list = []
    if get_status and len(data) > 0:
        for item in data['Protocols']:
            registration_number = item['number']
            date_time = item['date']

            entry_date = departure_date = is_on_station = None

            if server_id == '4' and item['direction'] == '1':
                entry_date = date_time
                is_on_station = True
            if server_id == '4' and item['direction'] == '2':
                departure_date = date_time
                is_on_station = False
            if server_id == '5' and item['direction'] == '2':
                entry_date = date_time
                is_on_station = True
            if server_id == '5' and item['direction'] == '1':
                departure_date = date_time
                is_on_station = False

            out_list.append({
                'registration_number': registration_number,
                'entry_date': convert_string_to_time(entry_date) if entry_date is not None else None,
                'departure_date': convert_string_to_time(departure_date) if departure_date is not None else None,
                'is_on_station': is_on_station
            })

    return out_list


def truck_processing():
    print('start truck_processing')
    video_server_list = ["4", "5"]
    for server in video_server_list:
        print(f'server -  {server}')

        truck_list = get_checkpoint_numbers(server, START_TIME) # получаем от "Интеллекта" список номеров с данными фотофиксации
        for truck in truck_list:

            registration_number = truck['registration_number']

            if not registration_number[0].isdigit(): # если номер начинается с цифры, значит это легковая машина - пропускаем обработку
                entry_date = entry_time = departure_date = departure_time = None
                print(f'registration_number is {registration_number} - ok')

                if truck['entry_date'] is not None:
                    entry_date, entry_time = convert_time_to_string(truck['entry_date'])
                if truck['departure_date'] is not None:
                    departure_date, departure_time = convert_time_to_string(truck['departure_date'])

                trucks_found, trucks_data = to_django.get_truck(registration_number)    # проверяем наличие в базе машины с данным номером
                if trucks_found:
                    print('truck found')
                    for item in trucks_data:
                        item['entry_date'] = entry_date
                        item['entry_time'] = entry_time
                        item['departure_date'] = departure_date
                        item['departure_time'] = departure_time
                        to_django.update_truck(item)
                        print('update_truck', truck['registration_number'])
                else:
                    new_truck_data = {
                        'registration_number': registration_number,
                        'entry_date': entry_date,
                        'entry_time': entry_time,
                        'departure_date': departure_date,
                        'departure_time': departure_time
                    }
                    to_django.create_truck(new_truck_data)
                    print('create_truck', truck['registration_number'])


schedule.every(5).minutes.do(truck_processing)
#schedule.every(10).seconds.do(truck_processing)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
