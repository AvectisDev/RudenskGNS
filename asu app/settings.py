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
        'delta_minutes': 3
    },
    {
        'id': '2,3',
        'delta_minutes': 30
    },
    {
        'id': '4,5',
        'delta_minutes': 3
    }
]

# OPC tags
class Railway:
    def __init__(self):
        self.tank_weight = 0.0
        self.camera_worked = False
        self.last_number = None
        self.tank_is_on_station = False
        self.complete = False


RAILWAY = {
    'tank_weight': 0.0,
    'camera_worked': False,
    'last_number': '',
    'complete': False,
    'tank_is_on_station': False
}


class Auto:
    def __init__(self):
        self.batch_type = None
        self.gas_type = 0  # Тип газа: 1 - Не выбран, 2 - СПБТ, 3 - ПБА
        self.batch_id = 0
        self.truck_id = None
        self.trailer_id = None
        self.initial_mass_meter = 0
        self.final_mass_meter = 0
        self.gas_amount = 0
        self.truck_full_weight = 0
        self.truck_empty_weight = 0
        self.weight_gas_amount = 0
        self.truck_capacity = 0
        self.request_number_identification = False
        self.response_number_detect = False
        self.request_batch_complete = False
        self.response_batch_complete = False

    def reset(self):
        """Сбросить атрибуты к их начальному значению."""
        self.batch_type = None
        self.gas_type = 0
        self.batch_id = 0
        self.truck_id = None
        self.trailer_id = None
        self.initial_mass_meter = 0
        self.final_mass_meter = 0
        self.gas_amount = 0
        self.truck_full_weight = 0
        self.truck_empty_weight = 0
        self.weight_gas_amount = 0
        self.truck_capacity = 0
        self.request_number_identification = False
        self.response_number_detect = False
        self.request_batch_complete = False
        self.response_batch_complete = False

    def update_truck_weights(self, full_weight, empty_weight):
        """Обновить веса грузовика."""
        self.truck_full_weight = full_weight
        self.truck_empty_weight = empty_weight


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
