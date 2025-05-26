import requests
import json
from typing import Dict, List, Optional, Union
from collections import defaultdict
import logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from functools import lru_cache
import time

from .utils import (
    validate_text, make_request, ServiceError,
    create_session, chunk_text, CSRF_TOKEN
)

from constants import SERVER, SENTIMENT_ANALYSIS

logger = logging.getLogger()

# Configuration
CHUNK_SIZE = 500
OVERLAP_SIZE = 50
MAX_RETRIES = 3
TIMEOUT = 30
CACHE_SIZE = 1000

class SentimentAnalysisError(Exception):
    """Custom exception for sentiment analysis errors."""
    pass

def process_chunk(chunk: str, session: requests.Session, url: str, headers: Dict[str, str]) -> Optional[Dict]:
    """Process a single chunk of text."""
    try:
        response = session.post(
            url,
            headers=headers,
            data={'inText': chunk},
            timeout=TIMEOUT
        )
        response.raise_for_status()
        
        result = response.json().get('Result', [])
        if isinstance(result, dict):
            result = [result]  # Convert single dict to list of one dict
        return parse_item_to_mongo(result)
    except requests.RequestException as e:
        logger.error(f"Request failed for chunk: {str(e)}")
        raise SentimentAnalysisError(f"Failed to process chunk: {str(e)}")
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON response: {str(e)}")
        raise SentimentAnalysisError(f"Invalid response format: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error processing chunk: {str(e)}")
        raise SentimentAnalysisError(f"Unexpected error: {str(e)}")

def parse_item_to_mongo(items: List[Dict]) -> Optional[Dict[str, float]]:
    """Parse sentiment analysis results."""
    if not items:
        return None
        
    try:
        result = {}
        for item in items:
            if not isinstance(item, dict):
                continue
            for sentiment, score in item.items():
                if not isinstance(score, (int, float)):
                    continue
                if sentiment not in result:
                    result[sentiment] = 0
                result[sentiment] += float(score)
        return {k: round(v * 100, 2) for k, v in result.items()}
    except Exception as e:
        logger.error(f"Error parsing sentiment results: {str(e)}")
        raise SentimentAnalysisError(f"Failed to parse results: {str(e)}")

def average_and_normalize(chunk_results: List[Dict[str, float]]) -> Dict[str, float]:
    """Average and normalize sentiment scores."""
    if not chunk_results:
        return {}
        
    totals = defaultdict(float)
    counts = defaultdict(int)

    # Accumulate all sentiment scores
    for result in chunk_results:
        for label, value in result.items():
            totals[label] += value
            counts[label] += 1

    # Calculate averages
    averaged = {
        label: totals[label] / counts[label]
        for label in totals
    }

    # Normalize to sum to 100
    total_score = sum(averaged.values())
    if total_score == 0:
        return {}

    normalized = {
        label: round((score / total_score) * 100, 1)
        for label, score in averaged.items()
    }

    return dict(sorted(normalized.items(), key=lambda x: x[1], reverse=True))

def run(text: str) -> Dict[str, float]:
    """
    Run sentiment analysis on the input text.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Dict containing normalized sentiment scores
        
    Raises:
        SentimentAnalysisError: If analysis fails
        ValueError: If input is invalid
    """
    try:
        validate_text(text)
        
        url = SERVER + SENTIMENT_ANALYSIS
        headers = {
            'X-CSRFToken': CSRF_TOKEN  # Using token from configuration
        }
        
        session = create_session()
        chunks = chunk_text(text)
        all_results = []

        for chunk in chunks:
            try:
                result = process_chunk(chunk, session, url, headers)
                if result:
                    all_results.append(result)
            except SentimentAnalysisError as e:
                logger.error(f"Failed to process chunk: {str(e)}")
                continue

        if not all_results:
            logger.warning("No valid results obtained from any chunks")
            return {}

        return average_and_normalize(all_results)

    except Exception as e:
        logger.error(f"Sentiment analysis failed: {str(e)}")
        print((f"Sentiment analysis failed: {str(e)}"))
        raise SentimentAnalysisError(f"Analysis failed: {str(e)}")
    finally:
        if 'session' in locals():
            session.close()
