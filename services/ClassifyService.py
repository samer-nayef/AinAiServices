import json

from constants import SERVER, CLASSIFY, CLASSIFY_IN_CLASS, CLASSIFY_LABELS

import logging
logger = logging.getLogger()

def run(text):
    import requests

    url = SERVER + CLASSIFY

    payload = {
        'inText': text,
        'inClass': CLASSIFY_IN_CLASS}

    headers = {
        'X-CSRFToken': 'KTdvPydTnee58BcT50NZdkpGjuU1SNgcs'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    res = json.loads(response.text)

    dic = res['ClassifyResult']

    classifys = parse_item_to_mongo(dic)
    if classifys:
        print(classifys)
    return classifys


def parse_item_to_mongo(items):
    result = {}
    try:
        for item in items:
            for k, v in item.items():
                if float(v.rstrip('%')) > 10:
                    valueEN = {i for i in CLASSIFY_LABELS if CLASSIFY_LABELS[i] == k}
                    valueEN = ' '.join(valueEN)
                    result[valueEN] = int(v.rstrip('%'))
    except Exception as e:
        logger.info('classify service ' + str(e))
        print(e)
    return result
