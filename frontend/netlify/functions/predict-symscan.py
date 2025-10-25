"""
Netlify Serverless Function: SymScan (Symptom-based) Prediction
Endpoint: /.netlify/functions/predict-symscan
Method: POST
"""

import json
import logging
import sys
import os

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'shared'))

from model_config import MODEL_URLS
from model_loader import load_models
from prediction.sysscan_prediction import predict_symscan
from pydantic import BaseModel, Field, ValidationError
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SymScanData(BaseModel):
    """Pydantic model for SymScan input validation"""
    symptoms: List[str] = Field(..., min_length=1, description="List of symptoms.")


# Required model artifacts
REQUIRED_MODELS = [
    'symScan_sympton_classifier_model',
    'symScan_unique_symptoms',
    'symScan_int_to_disease_map',
    'symScan_precautions_map'
]


def handler(event, context):
    """Netlify serverless function handler for SymScan prediction."""
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}

    try:
        # Parse request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})

        logger.info("Received SymScan prediction request")

        # Validate input
        try:
            validated_data = SymScanData(**body).model_dump()
            user_symptoms = validated_data.get('symptoms')
        except ValidationError as e:
            logger.error(f"Validation error: {e.errors()}")
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Invalid input format for SymScan prediction',
                    'details': e.errors(),
                    'medical_disclaimer': 'This system is informational only.'
                })
            }

        # Load models
        logger.info("Loading SymScan models...")
        models_dict = load_models(MODEL_URLS, REQUIRED_MODELS)

        missing_models = [key for key in REQUIRED_MODELS if key not in models_dict]
        if missing_models:
            logger.error(f"Missing models: {missing_models}")
            return {
                'statusCode': 503,
                'headers': headers,
                'body': json.dumps({
                    'error': 'SymScan model not available',
                    'details': f'Missing: {missing_models}'
                })
            }

        # Prepare models for prediction
        symscan_models = {
            'symscan_model': models_dict.get('symScan_sympton_classifier_model'),
            'unique_symptoms': models_dict.get('symScan_unique_symptoms'),
            'int_to_disease_map': models_dict.get('symScan_int_to_disease_map'),
            'precautions_map': models_dict.get('symScan_precautions_map')
        }

        # Make prediction
        logger.info(f"Making SymScan prediction for symptoms: {user_symptoms}")
        result = predict_symscan(user_symptoms, symscan_models)

        logger.info("SymScan prediction successful")
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(result)
        }

    except Exception as e:
        logger.exception(f"Error in SymScan prediction: {e}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal server error',
                'details': str(e)
            })
        }
