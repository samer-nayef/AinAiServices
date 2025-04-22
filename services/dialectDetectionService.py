import json
import logging
import math

from constants import SERVER, DIALECT_DECT
import logging
logger = logging.getLogger()

def run(text):
    import requests

    url = SERVER + DIALECT_DECT

    payload = {'inText': text}

    headers = {'X-CSRFToken': 'KTdvPydTnee58BcT50NZdkpGjuU1SNgcs'}

    response = requests.request("POST", url, headers=headers, data=payload)
    res = json.loads(response.text)

    dic = res['Result']

    dialects = parse_item_to_mongo(dic)
    if dialects:
        print(dialects)
    else:
        dialects = {}
    return dialects


def parse_item_to_mongo(items):
    try:
        if not isinstance(items, list):
            raise ValueError("Input must be a list")

        return {k: round(v * 100) for item in items for k, v in item.items() if v > 0.3}
    except BaseException as e:
        logger.info('dialect detection service ' + str(e))
