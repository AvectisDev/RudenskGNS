import socket
import psycopg2
from datetime import datetime
import binascii
import time
from parameters import readers, COMMANDS


def write_nfc_tag(nfc_tag: str, status: str):
    """Функция записывает в базу данных номер метки и дату проведения операции считывания"""

    try:
        conn = psycopg2.connect(dbname="PinskGNS", host="localhost", user="postgres", password=".avectis1", port="5432")
        conn.autocommit = True

        with conn.cursor() as cursor:

            cursor.execute(f"SELECT * FROM public.filling_station_balloon "
                           f"WHERE nfc_tag = '{nfc_tag}'")
            balloon_id = cursor.fetchall()
            if len(balloon_id) == 0:  # если метки ещё нет в базе
                cursor.execute(f"INSERT INTO filling_station_balloon (nfc_tag, status) "
                               f"VALUES ('{nfc_tag}', '{status}')")

                cursor.execute(f"SELECT * FROM public.filling_station_balloon "
                               f"WHERE nfc_tag = '{nfc_tag}'")
                balloon_id = cursor.fetchall()
                print("Data added")
            else:
                cursor.execute(f"UPDATE public.filling_station_balloon "
                               f"SET status = '{status}' "
                               f"WHERE nfc_tag = '{nfc_tag}' and status <> '{status}'")
                print("Data updated")

            if balloon_id[0][9] != status:
                current_date = datetime.now()
                cursor.execute(
                    f"INSERT INTO filling_station_changeballoonstatus (change_status_date, change_status_time, status, balloon_id) "
                    f"VALUES ('{current_date.date()}', '{current_date.time()}', '{status}', '{balloon_id[0][0]}')")

        conn.close()
    except:
        print('Can`t establish connection to database')


def byte_reversal(byte_string: str):
    """Функция разворачивает принятые со считывателя байты в обратном порядке, меняя местами первый и последний байт,
    второй и предпоследний и т.д."""

    data_list = list(byte_string)
    k = -1
    for i in range((len(data_list) - 1) // 2):
        data_list[i], data_list[k] = data_list[k], data_list[i]
        k -= 1
    for i in range(0, len(data_list) - 1, 2):
        data_list[i], data_list[i + 1] = data_list[i + 1], data_list[i]
    return ''.join(data_list)


def data_exchange_with_reader(controller: dict, command: str):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(0.3)
            s.connect((controller['ip'], controller['port']))
            s.sendall(binascii.unhexlify(COMMANDS[command]))  # команда считывания метки

            data = s.recv(2048)
            buffer = binascii.hexlify(data).decode()
            print('Receive complete. Data from reader: ', buffer)
            return buffer
        except:
            print(f'Can`t establish connection with RFID reader {controller['ip']}:{controller['port']}')


def read_nfc_tag(reader: dict):
    """Функция отправляет запрос на считыватель FEIG и получает в ответ дату, время и номер RFID метки """

    previous_nfc_tag = reader['nfc_tag']  # присваиваем предыдущую метку временной переменной
    data = data_exchange_with_reader(reader, 'buffer_read')

    if len(data) > 18:  # если со считывателя пришли данные с меткой
        nfc_tag = byte_reversal(data[14:30])  # из буфера получаем номер метки
        if nfc_tag != previous_nfc_tag:     # и метка отличается от предыдущей
            write_nfc_tag(nfc_tag, reader['status'])
            data_exchange_with_reader(reader, 'read_complete')  # зажигаем зелёную лампу на считывателе
            return nfc_tag  # возвращаем значение новой считанной метки
        else:
            return previous_nfc_tag     # если была повторно считана прошлая метка
    else:
        return previous_nfc_tag     # если считыватель не определил метку


# Program
while True:
    for reader in readers:
        reader['nfc_tag'] = read_nfc_tag(reader)
        time.sleep(0.1)
