"""
Номера серверов "Интеллект":
    - Камера 23 (ЖД Весовая) -> "id": "1", direction = 3 - направо, 4 - налево
    - Камера 25 (Весовая автотранспорта 1) -> "id": "2"
    - Камера 26 (Весовая автотранспорта 2) -> "id": "3"
    - Камера 27 (Распознавание номеров КПП Выезд) -> "id": "4", direction = 1 - от камеры, 2 - к камере
    - Камера 28 (Распознавание номеров КПП Въезд) -> "id": "5", direction = 1 - от камеры, 2 - к камере
"""
INTELLECT_URL = "http://10.10.0.252:10001/lprserver/GetProtocolNumbers"  # intellect server address
INTELLECT_SERVER_LIST = [
    {
        'id': '1',
        'delta_minutes': 5
    },
    {
        'id': '2,3',
        'delta_minutes': 10
    },
    {
        'id': '4,5',
        'delta_minutes': 3
    }
]

# OPC tags
RAILWAY = {
    'tank_weight': 0.0,
    'weight_is_stable': False,
    'camera_worked': False,
    'last_number': '',
    'complete': False,
    'tank_id': None,
    'tank_full_weight': 0,
    'tank_empty_weight': 0,
    'weight_gas_amount': 0
}

AUTO = {
    'batch_type': None,
    'gas_type': 0,  # Тип газа.1-Не выбран, 2-СПБТ, 3-ПБА
    'batch_id': 0,
    'truck_id': None,
    'trailer_id': None,
    'initial_mass_meter': 0,
    'final_mass_meter': 0,
    'gas_amount': 0,
    'truck_full_weight': 0,
    'truck_empty_weight': 0,
    'weight_gas_amount': 0,
    'truck_capacity': 0,
    'request_number_identification': False,
    'response_number_detect': False,
    'request_batch_complete': False,
    'response_batch_complete': False
}
