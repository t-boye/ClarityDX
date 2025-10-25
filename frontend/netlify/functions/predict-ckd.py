"""
Netlify Serverless Function: Chronic Kidney Disease (CKD) Prediction
Endpoint: /.netlify/functions/predict-ckd
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
from prediction.ckd_prediction import predict_ckd
from pydantic import BaseModel, Field, ValidationError, conint, confloat
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CKDData(BaseModel):
    """Pydantic model for CKD input validation"""
    age_yrs: Optional[conint(ge=0)] = Field(default=None, alias="Age (yrs)")
    blood_pressure_mm_hg: Optional[confloat()] = Field(default=None, alias="Blood Pressure (mm/Hg)")
    specific_gravity: Optional[confloat()] = Field(default=None, alias="Specific Gravity")
    albumin: Optional[confloat()] = Field(default=None, alias="Albumin")
    sugar: Optional[confloat()] = Field(default=None, alias="Sugar")
    blood_glucose_random_mgs_dl: Optional[confloat()] = Field(default=None, alias="Blood Glucose Random (mgs/dL)")
    blood_urea_mgs_dl: Optional[confloat()] = Field(default=None, alias="Blood Urea (mgs/dL)")
    serum_creatinine_mgs_dl: Optional[confloat()] = Field(default=None, alias="Serum Creatinine (mgs/dL)")
    sodium_meq_l: Optional[confloat()] = Field(default=None, alias="Sodium (mEq/L)")
    potassium_meq_l: Optional[confloat()] = Field(default=None, alias="Potassium (mEq/L)")
    hemoglobin_gms: Optional[confloat()] = Field(default=None, alias="Hemoglobin (gms)")
    packed_cell_volume: Optional[confloat()] = Field(default=None, alias="Packed Cell Volume")
    white_blood_cells_cells_cmm: Optional[confloat()] = Field(default=None, alias="White Blood Cells (cells/cmm)")
    red_blood_cells_millions_cmm: Optional[confloat()] = Field(default=None, alias="Red Blood Cells (millions/cmm)")
    red_blood_cells_normal: Optional[conint(ge=0, le=1)] = Field(default=None, alias="Red Blood Cells: normal")
    pus_cells_normal: Optional[conint(ge=0, le=1)] = Field(default=None, alias="Pus Cells: normal")
    pus_cell_clumps_present: Optional[conint(ge=0, le=1)] = Field(default=None, alias="Pus Cell Clumps: present")
    bacteria_present: Optional[conint(ge=0, le=1)] = Field(default=None, alias="Bacteria: present")
    hypertension_yes: Optional[conint(ge=0, le=1)] = Field(default=None, alias="Hypertension: yes")
    diabetes_mellitus_yes: Optional[conint(ge=0, le=1)] = Field(default=None, alias="Diabetes Mellitus: yes")
    coronary_artery_disease_yes: Optional[conint(ge=0, le=1)] = Field(default=None, alias="Coronary Artery Disease: yes")
    appetite_poor: Optional[conint(ge=0, le=1)] = Field(default=None, alias="Appetite: poor")
    pedal_edema_yes: Optional[conint(ge=0, le=1)] = Field(default=None, alias="Pedal Edema: yes")
    anemia_yes: Optional[conint(ge=0, le=1)] = Field(default=None, alias="Anemia: yes")


# Required model artifacts
REQUIRED_MODELS = [
    'ckd_model',
    'ckd_scaler',
    'ckd_feature_names'
]


def handler(event, context):
    """
    Netlify serverless function handler for CKD prediction.

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

        logger.info(f"Received CKD prediction request")

        # Validate input with Pydantic
        try:
            validated_data = CKDData(**body).model_dump(by_alias=True)
        except ValidationError as e:
            logger.error(f"Validation error: {e.errors()}")
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Invalid input format for CKD prediction',
                    'details': e.errors(),
                    'medical_disclaimer': 'This system is informational only and not a substitute for professional medical advice.'
                })
            }

        # Load required models
        logger.info("Loading CKD models...")
        models_dict = load_models(MODEL_URLS, REQUIRED_MODELS)

        # Check if all required models are loaded
        missing_models = [key for key in REQUIRED_MODELS if key not in models_dict]
        if missing_models:
            logger.error(f"Missing required models: {missing_models}")
            return {
                'statusCode': 503,
                'headers': headers,
                'body': json.dumps({
                    'error': 'CKD model not available',
                    'details': f'Missing models: {missing_models}',
                    'medical_disclaimer': 'This system is informational only and not a substitute for professional medical advice.'
                })
            }

        # Make prediction
        logger.info("Making CKD prediction...")
        result = predict_ckd(validated_data, models_dict)

        logger.info("CKD prediction successful")

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(result)
        }

    except Exception as e:
        logger.exception(f"Unhandled error in CKD prediction: {e}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal server error during CKD prediction',
                'details': str(e),
                'medical_disclaimer': 'This system is informational only and not a substitute for professional medical advice.'
            })
        }
