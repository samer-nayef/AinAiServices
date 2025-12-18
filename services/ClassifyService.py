from typing import Dict, List, Optional
import logging

import runServices
from constants import CLASSIFY, CLASSIFY_IN_CLASS, CLASSIFY_LABELS
from .utils import (
    validate_text, make_request, ServiceError,
    create_session, chunk_text, average_and_normalize
)

logger = logging.getLogger()

def parse_classification(items: List[Dict]) -> Dict[str, int]:
    """
    Parse classification results.
    
    Args:
        items: List of classification results
        
    Returns:
        Dictionary mapping categories to their confidence scores
    """
    result = {}
    try:
        for item in items:
            for k, v in item.items():
                if float(v.rstrip('%')) > 10:
                    value_en = {i for i in CLASSIFY_LABELS if CLASSIFY_LABELS[i] == k}
                    value_en = ' '.join(value_en)
                    result[value_en] = int(v.rstrip('%'))
        return result
    except Exception as e:
        logger.error(f"Error parsing classification results: {str(e)}")
        raise ServiceError(f"Failed to parse classification results: {str(e)}")

def run(text: str) -> Dict[str, float]:
    """
    Classify the input text.
    
    Args:
        text: Input text to classify
        
    Returns:
        Dictionary mapping categories to their confidence scores
        
    Raises:
        ServiceError: If classification fails
        ValueError: If input is invalid
    """
    try:
        validate_text(text)
        
        url = runServices.cfg.get('urls','SERVER') + CLASSIFY
        session = create_session()
        chunks = chunk_text(text)
        all_results = []

        for chunk in chunks:
            try:
                response = make_request(
                    url,
                    {
                        'inText': chunk,
                        'inClass': CLASSIFY_IN_CLASS
                    },
                    session=session
                )
                
                results = response.get('ClassifyResult', [])
                classification = parse_classification(results)
                
                if classification:
                    all_results.append(classification)
                    
            except ServiceError as e:
                logger.error(f"Failed to process chunk: {str(e)}")
                continue

        if not all_results:
            logger.warning("No valid classification results obtained")
            return {}

        return average_and_normalize(all_results)

    except Exception as e:
        logger.error(f"Classification failed: {str(e)}")
        raise ServiceError(f"Classification failed: {str(e)}")
    finally:
        if 'session' in locals():
            session.close()
