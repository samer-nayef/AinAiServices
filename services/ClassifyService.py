from constants import SERVER, CLASSIFY, CLASSIFY_IN_CLASS, CLASSIFY_LABELS

import logging
import requests
import json

logger = logging.getLogger()

from collections import defaultdict



def run(text):
    url = SERVER + CLASSIFY
    headers = {
        'X-CSRFToken': 'KTdvPydTnee58BcT50NZdkpGjuU1SNgcs'
    }

    chunk_size = 500  # Safe size below token limit
    overlap = 50       # Optional overlap for smoother context
    chunks = [
        text[i:i + chunk_size]
        for i in range(0, len(text), chunk_size - overlap)
    ]

    all_results = []

    for chunk in chunks:
        payload = {
            'inText': chunk,
            'inClass': CLASSIFY_IN_CLASS
        }

        try:
            response = requests.post(url, headers=headers, data=payload)
            res = json.loads(response.text)
            dic = res.get('ClassifyResult', {})
            classifys = parse_item_to_mongo(dic)

            if classifys:
                # print(f"Chunk result: {classifys}")
                all_results.append(classifys)

        except Exception as e:
            print(f"Error processing chunk: {e}")
    final_result = average_and_normalize(all_results)

    return final_result


def average_and_normalize(chunk_results):
    totals = defaultdict(float)
    counts = defaultdict(int)

    # Accumulate all class scores
    for result in chunk_results:
        for label, value in result.items():
            totals[label] += value
            counts[label] += 1

    # Average per label
    averaged = {label: totals[label] / counts[label] for label in totals}

    # Normalize to sum to 100
    total_score = sum(averaged.values())
    normalized = {label: round((score / total_score) * 100, 1) for label, score in averaged.items()}

    # Sort by highest score
    return dict(sorted(normalized.items(), key=lambda x: x[1], reverse=True))



# def run(text):
#     import requests
#
#     url = SERVER + CLASSIFY
#
#     payload = {
#         'inText': text,
#         'inClass': CLASSIFY_IN_CLASS}
#
#     headers = {
#         'X-CSRFToken': 'KTdvPydTnee58BcT50NZdkpGjuU1SNgcs'
#     }
#
#     response = requests.request("POST", url, headers=headers, data=payload)
#     res = json.loads(response.text)
#
#     dic = res['ClassifyResult']
#
#     classifys = parse_item_to_mongo(dic)
#     if classifys:
#         print(classifys)
#     return classifys


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
