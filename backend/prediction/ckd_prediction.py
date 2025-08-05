import logging
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, confloat, conint, ValidationError
import joblib
import os
import requests
from typing import Optional, List, Dict, Union

# Configure logging (as before)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Environment URLs for CKD model artifacts
CKD_MODEL_URL = os.getenv("CKD_MODEL_URL")
CKD_SCALER_URL = os.getenv("CKD_SCALER_URL")
CKD_FEATURE_NAMES_URL = os.getenv("CKD_FEATURE_NAMES_URL")

# Global instances
ckd_model_instance = None
ckd_scaler_instance = None
ckd_feature_names_list = None

def load_ckd_model_components():
    """
    Attempts to load model components from the specified remote URLs.
    This function will raise an exception because joblib cannot directly
    load from a URL.
    """
    raise NotImplementedError(
        "Model components cannot be loaded directly from URLs using joblib. "
        "Please use a separate model-serving API or download the files "
        "and load them locally or in-memory."
    )

# The attempt to load models here will now raise the exception,
# preventing the application from starting if this function is called.
# You should handle this at the application startup level.
# For this example, we will remove the direct call to `load_ckd_model_components()`
# and assume an external mechanism handles model loading.

class CKDData(BaseModel):
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

def generate_ckd_diagnosis_message(prediction: int, probabilities: List[float], input_data: pd.DataFrame) -> Dict[str, Union[str, Dict]]:
    diagnosis_messages = {
        0: "Low likelihood of Chronic Kidney Disease (CKD) detected. ✅",
        1: "High likelihood of Chronic Kidney Disease (CKD) detected. ❗️ Further evaluation is strongly recommended."
    }

    diagnosis = diagnosis_messages.get(prediction, "Uncertain CKD status.")
    explanation = {
        "overall_assessment": diagnosis,
        "probability_ckd": probabilities[1]
    }

    if isinstance(input_data, pd.DataFrame) and not input_data.empty:
        input_dict = input_data.iloc[0].to_dict()
    else:
        input_dict = {}

    significant_factors = []

    if (age := input_dict.get('Age (yrs)')) is not None and age > 60:
        significant_factors.append(f"Elevated age ({age} years)")

    if (bp := input_dict.get('Blood Pressure (mm/Hg)')) is not None and bp > 140:
        significant_factors.append(f"Elevated blood pressure ({bp} mm/Hg)")

    if (alb := input_dict.get('Albumin')) is not None and alb > 3.5:
        significant_factors.append(f"Elevated albumin ({alb})")

    if (sug := input_dict.get('Sugar')) is not None and sug > 2:
        significant_factors.append(f"Elevated sugar level ({sug})")

    if (scr := input_dict.get('Serum Creatinine (mgs/dL)')) is not None and scr > 1.2:
        significant_factors.append(f"Elevated serum creatinine ({scr} mg/dL)")

    if (hgb := input_dict.get('Hemoglobin (gms)')) is not None and hgb < 10:
        significant_factors.append(f"Low hemoglobin level ({hgb} gms)")

    if input_dict.get('Hypertension: yes') == 1:
        significant_factors.append("History of hypertension")
    if input_dict.get('Diabetes Mellitus: yes') == 1:
        significant_factors.append("History of diabetes mellitus")
    if input_dict.get('Coronary Artery Disease: yes') == 1:
        significant_factors.append("History of coronary artery disease")
    if input_dict.get('Appetite: poor') == 1:
        significant_factors.append("Poor appetite reported")
    if input_dict.get('Pedal Edema: yes') == 1:
        significant_factors.append("Presence of pedal edema")
    if input_dict.get('Anemia: yes') == 1:
        significant_factors.append("Presence of anemia")

    explanation["significant_risk_factors"] = {
        "message": "Significant risk factors identified:" if significant_factors else "No significant risk factors identified based on the model's criteria.",
        "factors": significant_factors if significant_factors else []
    }

    explanation["disclaimer"] = "This is a prediction, not a definitive diagnosis. Consult a healthcare professional."

    return {"diagnosis": diagnosis, "explanation": explanation}


def predict_ckd(data: Dict) -> Dict:
    """
    Processes input data and sends it to an external prediction API endpoint.
    """
    logger.info(f"CKD prediction request: {data}")

    try:
        # Validate the input data using the Pydantic model
        validated_data = CKDData.model_validate(data)
        input_data_for_api = validated_data.model_dump(by_alias=True)
        logger.info(f"Validated CKD input for API call: {input_data_for_api}")
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        return {"error": f"Invalid input: {e.errors()}", "status_code": 400}

    # Here's the core change: Instead of using local models, we call an API
    # Replace `PREDICTION_API_URL` with your actual endpoint.
    PREDICTION_API_URL = os.getenv("CKD_PREDICTION_API_URL", "http://your-prediction-api.com/predict")

    try:
        # Send the processed data to the prediction API
        response = requests.post(PREDICTION_API_URL, json=input_data_for_api, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        prediction_result = response.json()
        logger.info(f"Received prediction from API: {prediction_result}")
        
        # The API's response should contain the prediction and probabilities
        prediction = prediction_result.get("prediction")
        probabilities = prediction_result.get("probabilities")
        
        if prediction is None or probabilities is None:
            logger.error("API response missing 'prediction' or 'probabilities' key.")
            return {"error": "Invalid response from prediction API", "status_code": 500}

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to connect to prediction API: {e}")
        return {"error": "Failed to connect to CKD prediction service", "status_code": 503}
    except Exception as e:
        logger.error(f"An unexpected error occurred during API call: {e}")
        return {"error": "An internal error occurred", "status_code": 500}

    # Generate a more user-friendly message based on the API's output
    # For this to work, we need the original input_df for the message function.
    # A cleaner approach would be for the API to return the message directly.
    # Let's create a dummy input_df to pass to the message generator.
    input_df = pd.DataFrame([input_data_for_api])
    diagnosis_info = generate_ckd_diagnosis_message(prediction, probabilities, input_df)
    
    # Combine the prediction and the generated message for the final payload
    response_payload = {
        "prediction": prediction,
        "probabilities": probabilities,
        "class_names": ["No CKD", "CKD"],
        **diagnosis_info  # Unpack the diagnosis_info dict into the main payload
    }

    logger.info(f"CKD prediction completed: {response_payload}")

    return response_payload