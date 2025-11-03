from typing import Dict, Optional
import logging

import runServices
from constants import TRANSLATE, TRANSLATE_IN_LANGUAGE
from .utils import validate_text, make_request, ServiceError

logger = logging.getLogger()

def run(text: str) -> Optional[Dict]:
    """
    Translate the input text.
    
    Args:
        text: Input text to translate
        
    Returns:
        Translation results or None if translation fails
        
    Raises:
        ServiceError: If translation fails
        ValueError: If input is invalid
    """
    try:
        validate_text(text)
        
        url = runServices.cfg.get('urls','SERVER') + TRANSLATE
        response = make_request(
            url,
            {
                'inText': text,
                'inLanguages': TRANSLATE_IN_LANGUAGE
            }
        )
        
        return response.get('translateResult')
        
    except Exception as e:
        logger.error(f"Translation failed: {str(e)}")
        raise ServiceError(f"Translation failed: {str(e)}")
