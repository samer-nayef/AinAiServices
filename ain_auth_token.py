import requests

import runServices


def get_token():
    username = runServices.USERNAME
    password = runServices.PASSWORD

    if not username or not password:
        return ("Username and Password are REQUIRED")


    url = runServices.WILDFLY_URL + runServices.LOGIN_URL
    payload = {
        "username": username,
        "password": password
    }
    headers = {
        "Content-Type": "application/json"
    }

    # disable SSL verification because localhost + self-signed certs
    response = requests.post(url, json=payload, headers=headers, verify=False)

    response.raise_for_status()  # blows up if login fails

    return response.json()  # usually contains token



