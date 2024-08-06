import socket
import psycopg2
from datetime import datetime, date, time
import binascii
import time
from RFID_parameter import readers, COMMANDS


def write_nfc_tag(nfc_tag: str, status: str):
    """Функция записывает в базу данных номер метки и дату проведения операции считывания"""

    try:
        conn = psycopg2.connect(dbname="PinskGNS", host="localhost", user="postgres", password=".avectis1", port="5432")
        conn.autocommit = True

        with conn.cursor() as cursor:
            
            cursor.execute(f"SELECT * FROM public.filling_station_balloon "
                            f"WHERE nfc_tag = '{nfc_tag}'")
            balloon_id = cursor.fetchall()
            if len(balloon_id) == 0: # если метки ещё нет в базе
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
                cursor.execute(f"INSERT INTO filling_station_changeballoonstatus (change_status_date, change_status_time, status, balloon_id) " 
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


def read_nfc_tag(reader: dict, command: dict):
    """Функция отправляет запрос на считыватель FEIG и получает в ответ дату, время и номер RFID метки """

    previous_nfc_tag = reader['nfc_tag']  # присваиваем предыдущую метку временной переменной

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        try:
            s.settimeout(0.2)
            s.connect((reader['ip'], reader['port']))
            s.sendall(binascii.unhexlify(command['buffer_read']))  # команда считывания метки

            data = s.recv(2048)
            data_bytes = binascii.hexlify(data)
            buffer = data_bytes.decode()
            print('Receive complete. Data from reader: ', buffer)

            if len(buffer) > 18:
                nfc_tag = byte_reversal(buffer[14:30])  # из буфера получаем новую метку

                if nfc_tag != previous_nfc_tag:
                    write_nfc_tag(nfc_tag, reader['status'])
                    s.sendall(binascii.unhexlify(command['read_complete']))  # зажигаем зелёную лампу на считывателе
            else:
                nfc_tag = previous_nfc_tag

            return nfc_tag  # из функции возвращаем значение считанной метки
        except:
            print(f'Can`t establish connection with RFID reader {reader['ip']}:{reader['port']}')
            return previous_nfc_tag


# Program
while True:
    for reader in readers:
        reader['nfc_tag'] = read_nfc_tag(reader, COMMANDS)
        time.sleep(0.1)
