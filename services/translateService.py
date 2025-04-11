import json

from constants import SERVER, TRANSLATE, TRANSLATE_IN_LANGUAGE


def run(text):
    import requests

    url = SERVER + TRANSLATE

    payload = {'inText': text,
               'inLanguages': TRANSLATE_IN_LANGUAGE}
    headers = {'X-CSRFToken': 'KTdvPydTnee58BcT50NZdkpGjuU1SNgcs'}

    response = requests.request("POST", url, headers=headers, data=payload)
    res = json.loads(response.text)

    dic = res['translateResult']

    return dic
