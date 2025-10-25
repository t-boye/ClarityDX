"""
Netlify Serverless Function: Malaria Image Processing
Endpoint: /.netlify/functions/process-malaria-image
Method: POST
Accepts: multipart/form-data with image file
"""

import json
import logging
import sys
import os
import base64

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'shared'))

from model_config import MODEL_URLS
from model_loader import load_models
from prediction.malaria_prediction import predict_malaria
from services.image_processing_service import process_image as process_malaria_image_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Required model artifacts
REQUIRED_MODELS = [
    'malaria_model'
]


def handler(event, context):
    """Netlify serverless function handler for malaria image processing."""
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}

    try:
        logger.info("Received malaria image processing request")

        # Load models
        logger.info("Loading malaria model...")
        models_dict = load_models(MODEL_URLS, REQUIRED_MODELS)

        missing_models = [key for key in REQUIRED_MODELS if key not in models_dict]
        if missing_models:
            logger.error(f"Missing models: {missing_models}")
            return {
                'statusCode': 503,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Malaria model not available',
                    'details': f'Missing: {missing_models}'
                })
            }

        # Call the prediction function
        # Note: The predict_malaria function expects a Flask request-like object
        # We need to adapt it for Netlify Functions

        # For Netlify Functions, the event contains the request data
        # We'll need to modify predict_malaria or create an adapter

        # Temporary response - this needs proper multipart form data handling
        response, status_code = predict_malaria(
            models=models_dict,
            process_image=process_malaria_image_data
        )

        return {
            'statusCode': status_code,
            'headers': headers,
            'body': json.dumps(response) if isinstance(response, dict) else response
        }

    except Exception as e:
        logger.exception(f"Error in malaria image processing: {e}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal server error',
                'details': str(e),
                'medical_disclaimer': 'This system is informational only.'
            })
        }
