import socket
import psycopg2
import datetime
import binascii
import time
from RFID_parameter import readers, COMMANDS


def write_nfc_tag(nfc_tag:str, status:str):
    """функция записывает в базу данных номер метки и дату проведения операции считывания"""

    try:
        conn =  psycopg2.connect(dbname="PinskGNS", host="localhost", user="postgres", password=".avectis1", port="5432")
        conn.autocommit = True

        with conn.cursor() as cursor:
            data = (nfc_tag, status, datetime.datetime.now())
            cursor.execute("INSERT INTO filling_station_ballon (nfc_tag, state, creation_date) VALUES (%s, %s, %s)", data)
            print("Data added")

        conn.close()
    
    except:
        print('Can`t establish connection to database')


def read_nfc_tag(reader:dict, command:dict):
    """функция отправляет запрос на считыватель FEIG и получает в ответ дату, время и номер RFID метки """

    previous_nfc_tag = reader['nfc_tag']    # присваиваем предыдущую метку временной переменной

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        
        try:
            s.settimeout(0.2)
            # print(f"Connecting to {reader['ip']}:{reader['port']}")
            s.connect((reader['ip'], reader['port']))  

            #send data to FEIG
            s.sendall(binascii.unhexlify(command['buffer_read'])) #команда считывания метки

            data = s.recv(2048)
            data_bytes = binascii.hexlify(data)
            buffer = data_bytes.decode()
            print('Recive complete. Data from reader: ', buffer)

            if len(buffer) > 18:
                nfc_tag = buffer[14:30]  # из буфера получаем новую метку
                if nfc_tag != previous_nfc_tag:
                    write_nfc_tag(nfc_tag, reader['status'])
                    s.sendall(binascii.unhexlify(command['read_complete'])) #зажигаем зелёную лампу на считывателе
                    # print(nfc_tag)
            else:
                nfc_tag = previous_nfc_tag
                
            return nfc_tag  #из функции возвращаем значение считанной метки
        except:
            print(f'Can`t establish connection with RFID reader {reader['ip']}:{reader['port']}')
            return previous_nfc_tag


# Program
while True:
    for reader in readers:
        reader['nfc_tag'] = read_nfc_tag(reader, COMMANDS)
        # print(f'nfc tag is {reader['nfc_tag']}\n')
        time.sleep(0.1)
