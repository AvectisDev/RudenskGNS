import requests


def get_balloon_by_nfc_tag(nfc_tag):
    url = f'https://publicapi-vitebsk.cloud.gas.by/getballoonbynfctag?nfctag={nfc_tag}&realm=brestoblgas'
    try:
        response = requests.get(url, timeout=1)
        return (True, response.json()['List']) if response.status_code == 200 else (False, {"status": "no data"})
    except:
        return False, {"status": "no data"}


def search_balloon_by_nfc_tag(nfc_tag):
    url = f'https://publicapi-vitebsk.cloud.gas.by/searchballoonbynfctag?nfctag={nfc_tag}&realm=brestoblgas'
    headers = {
        'accept': 'application/json',
        'Authorization': 'Basic cGluc2tyZmlkZ25zOlhpbzhCemgzY0JRa0xtNQ=='
    }
    try:
        response = requests.get(url, headers=headers, timeout=1)
        return (True, response.json()['List']) if response.status_code == 200 else (False, {"status": "no data"})
    except:
        return False, {"status": "no data"}
