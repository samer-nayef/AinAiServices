from typing import Dict, Optional
import logging

from constants import SERVER, SUMMARIZE
from .utils import validate_text, make_request, ServiceError

logger = logging.getLogger()

def run(text: str) -> Optional[str]:
    """
    Generate a summary for the input text.
    
    Args:
        text: Input text to summarize
        
    Returns:
        Summary text or None if summarization fails
        
    Raises:
        ServiceError: If summarization fails
        ValueError: If input is invalid
    """
    try:
        validate_text(text)
        
        url = SERVER + SUMMARIZE
        response = make_request(url, {'inText': text})
        
        return response.get('SummarizationResult')
        
    except Exception as e:
        logger.error(f"Summarization failed: {str(e)}")
        raise ServiceError(f"Summarization failed: {str(e)}")