import requests
import json

from constants import SERVER, SENTIMENT_ANALYSIS
import logging

from collections import defaultdict


logger = logging.getLogger()

def run(text):

    url = SERVER + SENTIMENT_ANALYSIS
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

    # Process each chunk
    for chunk in chunks:
        payload = {'inText': chunk}

        try:
            response = requests.post(url, headers=headers, data=payload)
            res = json.loads(response.text)
            dic = res.get('Result', {})

            # Parse sentiment data
            senti = parse_item_to_mongo(dic)

            if senti:
                # print(f"Chunk result: {senti}")
                all_results.append(senti)

        except Exception as e:
            print(f"Error processing chunk: {e}")

    # After processing all chunks, average and normalize results
    final_result = average_and_normalize(all_results)

    return final_result


def average_and_normalize(chunk_results):
    totals = defaultdict(float)
    counts = defaultdict(int)

    # Accumulate all sentiment scores
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
#     url = SERVER + SENTIMENT_ANALYSIS
#
#     payload = {'inText': text}
#
#     headers = {'X-CSRFToken': 'KTdvPydTnee58BcT50NZdkpGjuU1SNgcs'}
#
#     response = requests.request("POST", url, headers=headers, data=payload)
#
#     res = json.loads(response.text)
#
#     dic = res['Result']
#     senti = parse_item_to_mongo(dic)
#     if senti:
#         print(senti)
#     return senti


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
