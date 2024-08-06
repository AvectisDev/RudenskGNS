import requests


def get_balloon_by_nfc_tag(nfc_tag):
    url = f'https://publicapi-vitebsk.cloud.gas.by/getballoonbynfctag?nfctag={nfc_tag}&realm=brestoblgas'
    try:
        response = requests.get(url, timeout=1)
        if response.status_code == 200:
            return response.json()
        else:
            return {"Status": "No data"}
    except:
        return {"Status": "No data"}


def search_balloon_by_nfc_tag(nfc_tag):
    url = f'https://publicapi-vitebsk.cloud.gas.by/searchballoonbynfctag?nfctag={nfc_tag}&realm=brestoblgas'
    headers = {
        'accept': 'application/json',
        'Authorization': 'Basic cGluc2tyZmlkZ25zOlhpbzhCemgzY0JRa0xtNQ=='
    }
    try:
        response = requests.get(url, headers=headers, timeout=1)
        if response.status_code == 200:
            return response.json()
        else:
            return {"Status": "No data"}
    except:
        return {"Status": "No data"}


print(search_balloon_by_nfc_tag("1c48ca0f5c0104e0"))
