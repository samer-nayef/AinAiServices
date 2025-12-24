import requests

import runServices
import base64, json
from datetime import datetime
import time


AIN_AUTH_TOKEN = None


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

    return response.json()["token"]  # usually contains token


def jwt_payload(token: str) -> dict:
    payload_b64 = token.split('.')[1]
    payload_b64 += '=' * (-len(payload_b64) % 4)
    return json.loads(base64.urlsafe_b64decode(payload_b64))


def is_token_expired(token, skew=60):
    payload = jwt_payload(token)
    return time.time() > payload["exp"] - skew


def get_valid_token():
    """
    Always returns a valid JWT.
    Automatically refreshes when expired or missing.
    """
    global AIN_AUTH_TOKEN

    if not AIN_AUTH_TOKEN:
        AIN_AUTH_TOKEN = get_token()
        _log_expiry(AIN_AUTH_TOKEN)
        return AIN_AUTH_TOKEN

    if is_token_expired(AIN_AUTH_TOKEN):
        print("🔄 JWT expired, refreshing...")
        AIN_AUTH_TOKEN = get_token()
        _log_expiry(AIN_AUTH_TOKEN)

    return AIN_AUTH_TOKEN


def _log_expiry(token: str):
    payload = jwt_payload(token)
    exp = datetime.fromtimestamp(payload["exp"])
    print(f"✅ JWT acquired, expires at {exp}")