READER_LIST = [{} for i in range(10)]

# Считыватели на приёмке
READER_LIST[0] = {
    'ip': '10.10.2.10',
    'port': 10001,
    'number': 1,
    'status': 'Линия 1 - приёмка баллонов',
    'input_state': 0,
    'previous_nfc_tags': [],
    'function': 'loading',
}

READER_LIST[1] = {
    'ip': '10.10.2.11',
    'port': 10001,
    'number': 2,
    'status': 'Линия 1 - вход в наполнительный цех',
    'input_state': 0,
    'previous_nfc_tags': [],
    'function': 'unloading',
}

READER_LIST[2] = {
    'ip': '10.10.2.12',
    'port': 10001,
    'number': 3,
    'status': 'Линия 2 - приёмка баллонов',
    'input_state': 0,
    'previous_nfc_tags': [],
    'function': 'unloading',
}

READER_LIST[3] = {
    'ip': '10.10.2.13',
    'port': 10001,
    'number': 4,
    'status': 'Линия 2 - вход в наполнительный цех',
    'input_state': 0,
    'previous_nfc_tags': [],
    'function': 'unloading',
}

# Считыватели в цеху
READER_LIST[4] = {
    'ip': '10.10.2.14',
    'port': 10001,
    'number': 5,
    'status': 'Линия 1 - отбраковка перед каруселью',
    'input_state': 0,
    'previous_nfc_tags': [],
    'function': None,
}

READER_LIST[5] = {
    'ip': '10.10.2.15',
    'port': 10001,
    'number': 6,
    'status': 'Линия 2 - выход из карусели',
    'input_state': 0,
    'previous_nfc_tags': [],
    'function': 'loading',
}

# Считыватели в цеху
READER_LIST[6] = {
    'ip': '10.10.2.16',
    'port': 10001,
    'number': 7,
    'status': 'Линия 2 - отбраковка перед каруселью',
    'input_state': 0,
    'previous_nfc_tags': [],
    'function': None,
}

READER_LIST[7] = {
    'ip': '10.10.2.17',
    'port': 10001,
    'number': 8,
    'status': 'Линия 1 - выход из карусели',
    'input_state': 0,
    'previous_nfc_tags': [],
    'function': None,
}

READER_LIST[8] = {
    'ip': '10.10.2.18',
    'port': 10001,
    'number': 9,
    'status': 'Линия 1 - карусель',
    'input_state': 0,
    'previous_nfc_tags': [],
    'function': None,
}

READER_LIST[9] = {
    'ip': '10.10.2.19',
    'port': 10001,
    'number': 10,
    'status': 'Линия 2 - карусель',
    'input_state': 0,
    'previous_nfc_tags': [],
    'function': None,
}

# Команды, посылаемые на считыватель
COMMANDS = {
    'host_read': '020009ffb001001843',
    'read_complete': '02000DFF72010181010019236B',  # зажигаем зелёную лампу на считывателе на 2.5 сек
    'read_complete_with_error': '02000DFF720101810B0014BCC3',  # мигание зелёной лампы на считывателе 2 сек
    'buffer_read': '020009FFB02B005B9D',  # чтение буферной памяти
    'inputs_read': '020007FF746660',  # чтение состояния входов
    'all_buffer_read': '02000AFF2B0000FF89EB',  # чтение всего буфера
    'read_last_item_from_buffer': '02000AFF2B00FFFF4914',
    'clean_buffer': '020007FF325447'  # команда очистки буфера
}
# 02 00 08 FF B0 84 4F DB   Reader: RF-Warning - если нет данных с ридера
