"""
Netlify Serverless Function: Hepatitis C Prediction
Endpoint: /.netlify/functions/predict-hepatitis-c
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
from prediction.hepatitis_c_prediction import predict_hepatitis_c
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HepatitisCData(BaseModel):
    """Pydantic model for Hepatitis C input validation"""
    Age: float = Field(..., alias="Age")
    Sex: Union[int, str] = Field(..., alias="Sex")
    ALB: Optional[float] = Field(None, alias="ALB")
    ALP: Optional[float] = Field(None, alias="ALP")
    ALT: Optional[float] = Field(None, alias="ALT")
    AST: Optional[float] = Field(None, alias="AST")
    BIL: Optional[float] = Field(None, alias="BIL")
    CHE: Optional[float] = Field(None, alias="CHE")
    CHOL: Optional[float] = Field(None, alias="CHOL")
    CREA: Optional[float] = Field(None, alias="CREA")
    GGT: Optional[float] = Field(None, alias="GGT")
    PROT: Optional[float] = Field(None, alias="PROT")
    AST_ALT: Optional[float] = Field(None, alias="AST/ALT")
    AgeGroup_Middle: int = Field(..., alias="AgeGroup_Middle")
    AgeGroup_Old: int = Field(..., alias="AgeGroup_Old")


# Required model artifacts
REQUIRED_MODELS = [
    'hepatitis_c_model',
    'hepatitis_c_scaler',
    'hepatitis_c_feature_names'
]


def handler(event, context):
    """Netlify serverless function handler for Hepatitis C prediction."""
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

        logger.info("Received Hepatitis C prediction request")

        # Validate input
        try:
            validated_data = HepatitisCData(**body).model_dump(by_alias=True)
        except ValidationError as e:
            logger.error(f"Validation error: {e.errors()}")
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Invalid input format for Hepatitis C prediction',
                    'details': e.errors(),
                    'medical_disclaimer': 'This system is informational only.'
                })
            }

        # Load models
        logger.info("Loading Hepatitis C models...")
        models_dict = load_models(MODEL_URLS, REQUIRED_MODELS)

        missing_models = [key for key in REQUIRED_MODELS if key not in models_dict]
        if missing_models:
            logger.error(f"Missing models: {missing_models}")
            return {
                'statusCode': 503,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Hepatitis C model not available',
                    'details': f'Missing: {missing_models}'
                })
            }

        # Make prediction
        logger.info("Making Hepatitis C prediction...")
        result = predict_hepatitis_c(validated_data, models_dict)

        logger.info("Hepatitis C prediction successful")
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(result)
        }

    except Exception as e:
        logger.exception(f"Error in Hepatitis C prediction: {e}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal server error',
                'details': str(e)
            })
        }
