import json

from constants import SERVER, SENTIMENT_ANALYSIS
import logging
logger = logging.getLogger()

def run(text):
    import requests

    url = SERVER + SENTIMENT_ANALYSIS

    payload = {'inText': text}

    headers = {'X-CSRFToken': 'KTdvPydTnee58BcT50NZdkpGjuU1SNgcs'}

    response = requests.request("POST", url, headers=headers, data=payload)

    res = json.loads(response.text)

    dic = res['Result']
    senti = parse_item_to_mongo(dic)
    if senti:
        print(senti)
    return senti


def parse_item_to_mongo(items):
    n = dict()
    try:
        if items:
            for item in items:
                for k, v in item.items():
                    """valueEN = {i for i in CLASSIFY_LABELS if CLASSIFY_LABELS[i] == k}
                    valueEN = ' '.join(valueEN)"""
                    n[k] = round(v * 100)


    except BaseException as e:
        logger.info('sentiment analysis service ' + str(e))
        print(e)
    return n
