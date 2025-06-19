import logging
from typing import Dict, List, Optional, Union, Any
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from functools import lru_cache
import json
import configparser

logger = logging.getLogger()

# Load configuration
cfg = configparser.ConfigParser()
cfg.read('configuration.cfg')

# Text Processing Configuration
CHUNK_SIZE = cfg.getint('text_processing', 'CHUNK_SIZE')
OVERLAP_SIZE = cfg.getint('text_processing', 'OVERLAP_SIZE')

# HTTP Settings
MAX_RETRIES = cfg.getint('http_settings', 'MAX_RETRIES')
TIMEOUT = cfg.getint('http_settings', 'TIMEOUT')
CACHE_SIZE = cfg.getint('http_settings', 'CACHE_SIZE')

# Authentication
CSRF_TOKEN = cfg.get('token', 'csrf')

class ServiceError(Exception):
    """Base exception for all service errors."""
    pass

def create_session() -> requests.Session:
    """Create a session with retry mechanism."""
    session = requests.Session()
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def validate_text(text: str) -> bool:
    """Validate input text."""
    if not isinstance(text, str):
        raise ValueError("Input must be a string")
    if not text.strip():
        raise ValueError("Input text cannot be empty")
    return True

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP_SIZE) -> List[str]:
    """Split text into overlapping chunks."""
    if len(text) <= chunk_size:
        return [text]
    
    # Ensure overlap is not larger than chunk_size - 1
    overlap = min(overlap, chunk_size - 1)
    
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        # Move forward by chunk_size - overlap
        start += (chunk_size - overlap)
    return chunks

def make_request(
    url: str,
    data: Dict[str, Any],
    session: Optional[requests.Session] = None,
    timeout: int = TIMEOUT
) -> Dict:
    """Make an HTTP request with proper error handling."""
    headers = {'X-CSRFToken': CSRF_TOKEN}
    
    try:
        if session:
            response = session.post(url, headers=headers, data=data, timeout=timeout)
        else:
            response = requests.post(url, headers=headers, data=data, timeout=timeout)
        
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        raise ServiceError(f"Request failed: {str(e)}")
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON response: {str(e)}")
        raise ServiceError(f"Invalid response format: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise ServiceError(f"Unexpected error: {str(e)}")

def average_and_normalize(chunk_results: List[Dict[str, float]]) -> Dict[str, float]:
    """Average and normalize scores from multiple chunks."""
    if not chunk_results:
        return {}
        
    totals = {}
    counts = {}

    # Accumulate all scores
    for result in chunk_results:
        for label, value in result.items():
            totals[label] = totals.get(label, 0) + value
            counts[label] = counts.get(label, 0) + 1

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