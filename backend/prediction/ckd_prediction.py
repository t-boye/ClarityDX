import logging
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, confloat, conint, ValidationError
import joblib
import os
from typing import Optional, List, Dict, Union

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Paths to model components
# Get the directory of the current file (ckd_prediction.py)
CURRENT_FILE_DIR = os.path.dirname(os.path.abspath(__file__)) # This correctly gets C:\...\backend\prediction

# Go up one level to get to the 'backend' directory
BACKEND_ROOT_DIR = os.path.abspath(os.path.join(CURRENT_FILE_DIR, '..')) # This will correctly be C:\...\backend

# Now, construct the path to the main 'models' directory within 'backend'
BASE_MODEL_DIR = os.path.join(BACKEND_ROOT_DIR, "models") # This will correctly be C:\...\backend\models

CKD_MODEL_DIR = os.path.join(BASE_MODEL_DIR, "ckd_model") # This will correctly be C:\...\backend\models\ckd_model (CORRECT!)
CKD_MODEL_PATH = os.path.join(CKD_MODEL_DIR, "ckd_best_model_random_forest_classifier.pkl")
CKD_SCALER_PATH = os.path.join(CKD_MODEL_DIR, "ckd_scaler.pkl")
CKD_FEATURE_NAMES_PATH = os.path.join(CKD_MODEL_DIR, "ckd_feature_names.pkl")

# Global instances
ckd_model_instance = None
ckd_scaler_instance = None
ckd_feature_names_list = None

def load_ckd_model_components():
    """Load model, scaler, and feature names."""
    global ckd_model_instance, ckd_scaler_instance, ckd_feature_names_list
    try:
        if os.path.exists(CKD_MODEL_PATH):
            ckd_model_instance = joblib.load(CKD_MODEL_PATH)
            logger.info(f"CKD model loaded: {CKD_MODEL_PATH}")
        else:
            logger.error(f"CKD model not found: {CKD_MODEL_PATH}")

        if os.path.exists(CKD_SCALER_PATH):
            ckd_scaler_instance = joblib.load(CKD_SCALER_PATH)
            logger.info(f"CKD scaler loaded: {CKD_SCALER_PATH}")
        else:
            logger.error(f"CKD scaler not found: {CKD_SCALER_PATH}")

        if os.path.exists(CKD_FEATURE_NAMES_PATH):
            ckd_feature_names_list = joblib.load(CKD_FEATURE_NAMES_PATH)
            logger.info(f"CKD feature names loaded: {CKD_FEATURE_NAMES_PATH}")
        else:
            logger.error(f"CKD feature names not found: {CKD_FEATURE_NAMES_PATH}")

        if ckd_model_instance and ckd_scaler_instance and ckd_feature_names_list:
            logger.info("CKD model components loaded successfully.")
        else:
            logger.error("Failed to load all CKD model components.")
    except Exception as e:
        ckd_model_instance = None
        ckd_scaler_instance = None
        ckd_feature_names_list = None
        logger.error(f"Exception while loading CKD model components: {e}", exc_info=True)

# Load model components on import
load_ckd_model_components()

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

    # Ensure input_data is a DataFrame and extract the first (and likely only) row as a dictionary
    if isinstance(input_data, pd.DataFrame) and not input_data.empty:
        input_dict = input_data.iloc[0].to_dict()
    else:
        input_dict = {} # Fallback if input_data is not as expected

    significant_factors = []

    # Using .get() for safer access and handling of potentially missing keys
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

    # Check for presence of binary factors (1 for 'yes' or 'present')
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
    logger.info(f"CKD prediction request: {data}")

    if not all([ckd_model_instance, ckd_scaler_instance, ckd_feature_names_list]):
        logger.error("CKD model or scaler not loaded.")
        # Return a dictionary that the frontend can parse as an error, but without the extra wrapper
        return {"error": "CKD model or scaler not available", "status_code": 500}

    try:
        validated_data = CKDData.model_validate(data)
        # Convert Pydantic model to a dictionary with aliases resolved
        input_data_for_df = validated_data.model_dump(by_alias=True)
        logger.info(f"Validated CKD input (with aliases): {input_data_for_df}")
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        return {"error": f"Invalid input: {e.errors()}", "status_code": 400}

    # Create DataFrame using the resolved aliases
    input_df = pd.DataFrame([input_data_for_df])
    # Ensure all expected feature columns are present, fill missing with 0 or NaN as appropriate for scaling
    # It's better to fill with NaN and then let the scaler handle it (if it's designed to),
    # or apply an imputer BEFORE scaling if that was part of your training pipeline.
    # For now, let's stick to your original fill_value=np.nan and then fillna(0)
    input_df = input_df.reindex(columns=ckd_feature_names_list, fill_value=np.nan).fillna(0)


    logger.info(f"Input data before scaling:\n{input_df}")

    try:
        input_scaled = ckd_scaler_instance.transform(input_df)
        logger.info("Input scaled.")
    except Exception as e:
        logger.error(f"Scaling error: {e}")
        return {"error": "Scaling error", "status_code": 500}

    try:
        probabilities = ckd_model_instance.predict_proba(input_scaled)[0].tolist()
        prediction = int(np.argmax(probabilities))
        logger.info(f"Prediction: {prediction}, Probabilities: {probabilities}")
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return {"error": "Prediction error", "status_code": 500}

    response_payload = {
        "prediction": prediction,
        "probabilities": probabilities,
        "class_names": ["No CKD", "CKD"]
    }

    diagnosis_info = generate_ckd_diagnosis_message(prediction, probabilities, input_df)
    response_payload.update(diagnosis_info)

    logger.info(f"CKD prediction completed: {response_payload}")
    
    # *** IMPORTANT CHANGE HERE ***
    # Return the payload directly, without the outer "response" key and "status_code"
    # The HTTP status code will be handled by your FastAPI/Flask route
    # that calls this function (e.g., `return JSONResponse(content=response_payload, status_code=200)`).
    return response_payload