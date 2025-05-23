from constants import SERVER, SUMMARIZE, CLASSIFY_IN_CLASS, CLASSIFY_LABELS

import logging
import requests
import json

logger = logging.getLogger()

from collections import defaultdict



def run(text):
    import requests

    url = SERVER + SUMMARIZE

    payload = {'inText': text,}
    headers = {'X-CSRFToken': 'KTdvPydTnee58BcT50NZdkpGjuU1SNgcs'}

    response = requests.request("POST", url, headers=headers, data=payload)
    res = json.loads(response.text)

    dic = res['SummarizationResult']

    return dic