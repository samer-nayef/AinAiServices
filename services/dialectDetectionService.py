from typing import Dict, Optional
import logging

import runServices
from constants import DIALECT_DECT
from .utils import validate_text, make_request, ServiceError

logger = logging.getLogger()

def parse_dialects(items: list) -> Dict[str, float]:
    """
    Parse dialect detection results.
    
    Args:
        items: List of dialect detection results
        
    Returns:
        Dictionary mapping dialects to their confidence scores
    """
    try:
        if not isinstance(items, list):
            raise ValueError("Input must be a list")

        return {
            k: round(v * 100)
            for item in items
            for k, v in item.items()
            if v > 0.1
        }
    except Exception as e:
        logger.error(f"Error parsing dialect results: {str(e)}")
        raise ServiceError(f"Failed to parse dialect results: {str(e)}")

def run(text: str) -> Dict[str, float]:
    """
    Detect dialects in the input text.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Dictionary mapping dialects to their confidence scores
        
    Raises:
        ServiceError: If detection fails
        ValueError: If input is invalid
    """
    try:
        validate_text(text)
        
        # Limit text length for dialect detection
        text = text[:500]
        
        url = runServices.cfg.get('urls','SERVER') + DIALECT_DECT
        response = make_request(url, {'inText': text})
        
        results = response.get('Result', [])
        return parse_dialects(results)
        
    except Exception as e:
        logger.error(f"Dialect detection failed: {str(e)}")
        raise ServiceError(f"Dialect detection failed: {str(e)}")
