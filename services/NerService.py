from typing import Dict, List, Optional
import logging

import runServices
from constants import NER, NER_LABELS
from .utils import validate_text, make_request, ServiceError

logger = logging.getLogger()

def parse_entities(items: List[Dict]) -> Dict[str, str]:
    """
    Parse named entity recognition results.
    
    Args:
        items: List of NER results
        
    Returns:
        Dictionary mapping entity types to their values
    """
    result = {}
    try:
        for item in items:
            for k, v in item.items():
                value_en = {i for i in NER_LABELS if NER_LABELS[i] == v}
                value_en = ' '.join(value_en)
                
                # Clean entity text
                entity_text = str(k).replace(' ', '_').replace('#', ' ').replace('،', '')
                
                if value_en in result:
                    if entity_text not in result[value_en]:
                        result[value_en] = f"{result[value_en]} , {entity_text}"
                else:
                    result[value_en] = entity_text
                    
        return result
    except Exception as e:
        logger.error(f"Error parsing NER results: {str(e)}")
        raise ServiceError(f"Failed to parse NER results: {str(e)}")

def run(text: str) -> Dict[str, str]:
    """
    Perform named entity recognition on the input text.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Dictionary mapping entity types to their values
        
    Raises:
        ServiceError: If NER fails
        ValueError: If input is invalid
    """
    try:
        validate_text(text)
        
        url = runServices.cfg.get('urls','SERVER') + NER
        response = make_request(url, {'inText': text})
        
        results = response.get('NERResult', [])
        return parse_entities(results)
        
    except Exception as e:
        logger.error(f"NER failed: {str(e)}")
        raise ServiceError(f"NER failed: {str(e)}")
