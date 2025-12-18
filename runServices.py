import configparser
import json
import logging
import os
import sys
import time
from contextlib import contextmanager
from typing import List, Dict, Any

import requests

import ain_auth_token
from services import NerService, ClassifyService, dialectDetectionService, LanguageDetectionService, \
    sentimentAnalysisService, summarizationService

logging.basicConfig(
    level=logging.INFO,
    filename="debug.log",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
#os.chdir(os.path.dirname(sys.argv[0]))
cfg = configparser.ConfigParser()
cfg.read('configuration.cfg')


USERNAME = cfg.get('wildfly', 'username')
PASSWORD = cfg.get('wildfly', 'password')

WILDFLY_URL = cfg.get('wildfly','url')
LOGIN_URL = cfg.get('wildfly','login')
FETCH_VIDEOS_URL = WILDFLY_URL + cfg.get('wildfly','video_by_flags')
UPDATE_VIDEO_URL = WILDFLY_URL + cfg.get('wildfly','update_video')
YARAA_FLAG = cfg.get('video_flags', 'yaraa')
TRANSLATE_FLAG = cfg.get('video_flags', 'translated')
RAQIM_FLAG = cfg.get('video_flags', 'raqim')
Text_NOT_FOUND = "Text not found"
AIN_AUTH_TOKEN = None




def update_video(video_id, ner_result, classify_result, language_detection_result, dialect_detection_result, sentiment_analysis_result, summarization_result):

    print(f"[DEBUG] Updating video {video_id}...")
    payload = {
        "id": video_id,
        TRANSLATE_FLAG: True,
        YARAA_FLAG:True,
        RAQIM_FLAG:True,
        "videoDetails": {
            "raqimNerService": json.dumps(ner_result or ""),
            "raqimClassifyService": json.dumps(classify_result or ""),
            "raqimDetectLangService": json.dumps(language_detection_result or ""),
            "raqimDialectService": json.dumps(dialect_detection_result or ""),
            "raqimSentimentService": json.dumps(sentiment_analysis_result or ""),
            "raqimSummarizationService": json.dumps(summarization_result or "")
        }
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {AIN_AUTH_TOKEN}'
    }
    try:
        resp = requests.put(UPDATE_VIDEO_URL, headers=headers, json=payload, verify=False)
        if resp.status_code != 200:
            logger.error(f"Failed to update video {video_id}: {resp.status_code} {resp.text}")
            print(f"[ERROR] Failed to update video {video_id}: {resp.status_code}")
        else:
            print(f"[SUCCESS] Video {video_id} updated.")
    except requests.RequestException as e:
        logger.error(f"Exception updating video {video_id}: {e}")
        print(f"[ERROR] Exception updating video {video_id}: {e}")



def process_batch(rows: List[Dict[str, Any]]) -> None:
    """Process a batch of rows and update the database."""

    for row in rows:
        try:
            if row.get('videoDetails', None):
                id = row.get('id')
                text = row.get('videoDetails').get('artext')

                # Run all services

                ner_result = NerService.run(text=text)
                classify_result = ClassifyService.run(text=text)
                language_detection_result = LanguageDetectionService.run(text=text)
                dialect_detection_result = None
                if language_detection_result.lower() == 'ar':
                    dialect_detection_result = dialectDetectionService.run(text=text)

                sentiment_analysis_result = sentimentAnalysisService.run(text=text)
                summarization_result = summarizationService.run(text=text)

                # Update database

                try:
                    update_video(video_id=id,
                                 ner_result=ner_result,
                                 classify_result=classify_result,
                                 language_detection_result=language_detection_result,
                                 dialect_detection_result=dialect_detection_result,
                                 sentiment_analysis_result=sentiment_analysis_result,
                                 summarization_result=summarization_result)

                except Exception as e:
                    print(f"❌ Failed to update translation in DB for id {id}: {e}")
                    logger.error(f"❌ Failed to update translation in DB for id {id}: {e}")


                logger.info(f'Successfully processed record: {id}')
                print(f'Successfully processed record: {id}')

        except Exception as e:
            logger.error(f"Error processing record {id}: {str(e)}")
            continue


def raqim_video_text() -> None:
    while True:
                try:
                    params = {
                        YARAA_FLAG: 'true',
                        TRANSLATE_FLAG: 'true',
                        RAQIM_FLAG: 'false',
                    }
                    headers = {'Authorization': f'Bearer {AIN_AUTH_TOKEN}'}

                    print("[DEBUG] Fetching unprocessed videos...")

                    resp = requests.get(FETCH_VIDEOS_URL, headers=headers, params=params,
                                        timeout=20, verify=False)
                    try:
                        rows = resp.json()
                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse JSON from fetch: {resp.text}")
                        print("[ERROR] Failed to parse JSON from fetch")
                        rows = []


                    if not rows:
                        print("⏸️ No unprocessed videos. Sleeping for 5 minutes...")
                        logger.info("⏸️ No unprocessed videos. Sleeping for 5 minutes...")
                        time.sleep(300)
                        continue

                    # Process batch
                    process_batch(rows)

                except Exception as e:
                    logger.error(f"Error in main processing loop: {str(e)}")
                    time.sleep(60)  # Wait a minute before retrying

def runservice() -> None:
    """Main service runner with proper error handling."""
    try:
        raqim_video_text()
    except Exception as e:
        logger.error(f"Service error: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        AIN_AUTH_TOKEN = ain_auth_token.get_token().get('token')
        if not AIN_AUTH_TOKEN:
            logger.error("Failed to get AIN_AUTH_TOKEN")
            print("[ERROR] Failed to get AIN_AUTH_TOKEN")
            exit(1)

        print(f'[DEBUG] AIN_AUTH_TOKEN retrieved successfully === {AIN_AUTH_TOKEN}')

        runservice()
    except Exception as ex:
        logger.error(f'Service failed: {str(ex)}')
        print(f"An error occurred. Please check the logs. Error: {str(ex)}")


