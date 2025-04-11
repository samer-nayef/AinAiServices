import json
import logging
from collections import defaultdict

import requests

from constants import SERVER, NER, NER_LABELS
logger = logging.getLogger()

def run(text):
    url = SERVER + NER

    payload = {'inText': text}

    headers = {'X-CSRFToken': 'KTdvPydTnee58BcT50NZdkpGjuU1SNgcs'}

    response = requests.request("POST", url, headers=headers, data=payload)

    res = json.loads(response.text)

    dic = res['NERResult']
    ners = parse_item_to_mongo(dic)
    print(ners)
    return ners


def parse_item_to_mongo(items):
    result = dict()
    try:
        for item in items:
            for k, v in item.items():
                valueEN = {i for i in NER_LABELS if NER_LABELS[i] == v}
                valueEN = ' '.join(valueEN)
                if valueEN in result:
                    if str(k).replace(' ','_').replace('#',' ').replace('،','') not in result[valueEN]:
                        value = result.get(valueEN) + ' ' + str(k).replace(' ','_').replace('#',' ').replace('،','')
                        result[valueEN] = value
                    else:
                        pass
                else:
                    result[valueEN] = str(k).replace(' ','_').replace('#','').replace('،','')

    except BaseException as e:
        logger.info('ner service ' + str(e))
        print(e)
    return result
