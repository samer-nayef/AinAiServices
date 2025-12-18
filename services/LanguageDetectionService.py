from typing import Optional
import logging

import runServices
from constants import  LANG_DECT
from .utils import validate_text, make_request, ServiceError

logger = logging.getLogger()

def run(text: str) -> str:
    """
    Detect the language of the input text.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Detected language code or 'undefined' if detection fails
        
    Raises:
        ServiceError: If detection fails
        ValueError: If input is invalid
    """
    try:
        validate_text(text)
        
        # Limit text length for language detection
        text = text[:150]
        
        url = runServices.cfg.get('urls','SERVER') + LANG_DECT
        response = make_request(url, {'inText': text})
        
        language = response.get('LangResult', {}).get('lang')
        return language if language else 'undefined'
        
    except Exception as e:
        logger.error(f"Language detection failed: {str(e)}")
        raise ServiceError(f"Language detection failed: {str(e)}")
