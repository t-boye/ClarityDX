"""
Netlify Serverless Function: Heart Disease Prediction
Endpoint: /.netlify/functions/predict-heart-disease
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
from prediction.heart_disease_prediction import predict_heart_disease
from pydantic import BaseModel, Field, ValidationError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HeartDiseaseData(BaseModel):
    """Pydantic model for heart disease input validation"""
    age: float = Field(..., description="Age in years")
    sex: float = Field(..., description="Sex (1 = male; 0 = female)")
    cp: float = Field(..., description="Chest Pain Type (0-3)")
    trestbps: float = Field(..., description="Resting Blood Pressure (mm Hg)")
    chol: float = Field(..., description="Serum Cholestoral (mg/dl)")
    fbs: float = Field(..., description="Fasting Blood Sugar > 120 mg/dl (1 = true; 0 = false)")
    restecg: float = Field(..., description="Resting Electrocardiographic Results (0-2)")
    thalach: float = Field(..., description="Maximum Heart Rate Achieved")
    exang: float = Field(..., description="Exercise Induced Angina (1 = yes; 0 = no)")
    oldpeak: float = Field(..., description="ST depression induced by exercise relative to rest")
    slope: float = Field(..., description="Slope of the peak exercise ST segment")
    ca: float = Field(..., description="Number of major vessels (0-3) colored by flourosopy")
    thal: float = Field(..., description="Thalassemia (1 = fixed defect; 2 = normal; 3 = reversible defect)")


# Required model artifacts
REQUIRED_MODELS = [
    'heart_disease_model',
    'heart_disease_scaler',
    'heart_disease_feature_names',
    'heart_disease_pca',
    'heart_disease_polynomial_features'
]


def handler(event, context):
    """
    Netlify serverless function handler for heart disease prediction.

    Args:
        event: API Gateway event object
        context: Lambda context object

    Returns:
        Response object with statusCode, headers, and body
    """
    # Set CORS headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    # Handle OPTIONS request for CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }

    try:
        # Parse request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})

        logger.info(f"Received heart disease prediction request: {body}")

        # Validate input with Pydantic
        try:
            validated_data = HeartDiseaseData(**body).model_dump()
        except ValidationError as e:
            logger.error(f"Validation error: {e.errors()}")
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Invalid input format for Heart Disease prediction',
                    'details': e.errors(),
                    'medical_disclaimer': 'This system is informational only and not a substitute for professional medical advice.'
                })
            }

        # Load required models
        logger.info("Loading heart disease models...")
        models_dict = load_models(MODEL_URLS, REQUIRED_MODELS)

        # Check if all required models are loaded
        missing_models = [key for key in REQUIRED_MODELS if key not in models_dict]
        if missing_models:
            logger.error(f"Missing required models: {missing_models}")
            return {
                'statusCode': 503,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Heart Disease model not available',
                    'details': f'Missing models: {missing_models}',
                    'medical_disclaimer': 'This system is informational only and not a substitute for professional medical advice.'
                })
            }

        # Prepare models for prediction function
        heart_disease_models = {
            'rf_model': models_dict.get('heart_disease_model'),
            'scaler': models_dict.get('heart_disease_scaler'),
            'feature_names': models_dict.get('heart_disease_feature_names'),
            'pca': models_dict.get('heart_disease_pca'),
            'polynomial_features': models_dict.get('heart_disease_polynomial_features')
        }

        # Make prediction
        logger.info("Making prediction...")
        result = predict_heart_disease(validated_data, heart_disease_models)

        logger.info(f"Prediction successful: {result}")

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(result)
        }

    except Exception as e:
        logger.exception(f"Unhandled error in heart disease prediction: {e}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal server error during Heart Disease prediction',
                'details': str(e),
                'medical_disclaimer': 'This system is informational only and not a substitute for professional medical advice.'
            })
        }
