import json

import requests

from constants import SERVER, LANG_DECT
import logging
logger = logging.getLogger()

def run(text):
    try:
        url = SERVER + LANG_DECT

        payload = {'inText': text[:150]}

        headers = {'csrftoken': 'KTdvPydTnee58BcT50NZdkpGjuU1SNgc'}

        response = requests.request("POST", url, headers=headers, data=payload)
        res = json.loads(response.text)

        dic = res.get('LangResult', {}).get('lang')
        if dic:
            return dic
        else:
            return 'undefined'

    except BaseException as e:
        logger.info('language detection service ' + str(e))
