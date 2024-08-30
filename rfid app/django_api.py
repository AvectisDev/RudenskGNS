import requests


def get_batch_balloons(batch_type):
    url = f'http://10.10.12.253:8000/api/rfid/GetBatchBalloons?batch_type={batch_type}'
    # url = f'http://127.0.0.1:8000/api/rfid/GetBatchBalloons?batch_type={batch_type}'
    try:
        response = requests.get(url, timeout=1)
        if response.status_code == 200:
            if response.json()['status'] == "ok":
                return True, response.json()['batch_id']

            else:  # ['status'] == "error"
                return False, response.json()['error']
        else:
            return False, {"status": response.status_code}
    except KeyError:
        return False, {"status": "no valid response"}
    except:
        return False, {"status": "no valid response"}


def update_batch_balloons(batch_type, reader: dict):
    url = f'http://10.10.12.253:8000/api/rfid/UpdateBatchBalloons'
    # url = f'http://127.0.0.1:8000/api/rfid/UpdateBatchBalloons'
    data = {
        'batch_type': batch_type,
        'batch_id': reader['batch']['batch_id'],
        'balloons_list': reader['batch']['balloons_list']
    }
    try:
        response = requests.post(url, json=data, timeout=1)
        if response.status_code == 200:
            return True, {"status": "ok"}
        else:
            return False, {"status": response.status_code}
    except KeyError:
        return False, {"status": "no valid response"}
    except:
        return False, {"status": "no valid response"}


# data = {'batch_type': 'loading', 'batch': {'batch_id': 1, 'balloons_list': ['yr5e6', '1sdg', '2sdg', '3sdg']}}
# print(get_batch_balloons('loading'))
# print(update_batch_balloons('loading', data))
