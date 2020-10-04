import requests

url = 'https://api.iedred7584.com/eew/json/'


def earthquake():
    response = requests.get(url)
    earthquakeinfo = response.json()
    return earthquakeinfo
