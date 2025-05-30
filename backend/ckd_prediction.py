import logging
from flask import request, jsonify
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, confloat, conint, ValidationError
import joblib  # Added import for joblib
import os  # Added import for os
from typing import Optional, List, Dict, Union  # Import Optional and List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Automatically get the absolute path to the models, relative to this file
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # Adjust as necessary
MODEL_PATH = os.path.join(BASE_DIR, "models", "ckd_model", "ckd_model.pkl")  # Or .joblib, whichever is correct
SCALER_PATH = os.path.join(BASE_DIR, "models", "ckd_model", "ckd_scaler.pkl")  # Or .joblib
FEATURE_NAMES_PATH = os.path.join(BASE_DIR, "models", "ckd_model", "ckd_feature_names.pkl")

# Load the model, scaler, and feature names at application startup
try:
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        logging.info(f"CKD model loaded from: {MODEL_PATH}")
    else:
        logging.error(f"CKD model not found at: {MODEL_PATH}")
        model = None

    if os.path.exists(SCALER_PATH):
        scaler = joblib.load(SCALER_PATH)
        logging.info(f"Scaler loaded from: {SCALER_PATH}")
    else:
        logging.error(f"Scaler not found at: {SCALER_PATH}")
        scaler = None

    if os.path.exists(FEATURE_NAMES_PATH):
        feature_names = joblib.load(FEATURE_NAMES_PATH)
        logging.info(f"Feature names loaded from: {FEATURE_NAMES_PATH}")
    else:
        logging.error(f"Feature names not found at: {FEATURE_NAMES_PATH}")
        feature_names = None

    if model and scaler and feature_names:
        logging.info("CKD model, scaler, and feature names loaded successfully.")
    else:
        logging.error("Failed to load CKD model components.")

except Exception as e:
    model = None
    scaler = None
    feature_names = None
    logging.error(f"Error loading CKD model, scaler, or feature names: {e}", exc_info=True)


# Pydantic model for CKD data validation
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


def generate_diagnosis_message(prediction: int, probabilities: List[float], feature_names: List[str], input_data: pd.DataFrame) -> Dict[str, Union[str, Dict[str, Union[str, float]]]]:
    """
    Generates a detailed human-readable diagnosis message with explanations, incorporating risk factor analysis.

    Args:
        prediction (int): The model's prediction (0 = No CKD, 1 = CKD).
        probabilities (List[float]): The probabilities for each class.
        feature_names (List[str]): The names of the input features.
        input_data (pd.DataFrame): The input data used for prediction.

    Returns:
        Dict[str, Union[str, Dict[str, Union[str, float]]]]: A dictionary containing the diagnosis and explanation.
    """

    diagnosis_messages = {
        0: "Low likelihood of Chronic Kidney Disease (CKD) detected. ✅",
        1: "High likelihood of Chronic Kidney Disease (CKD) detected. ❗️ Further evaluation is strongly recommended."
    }
    diagnosis: str = diagnosis_messages.get(prediction, "Uncertain CKD status.")

    explanation: Dict[str, Union[str, Dict[str, Union[str, float]]]] = {}
    explanation["overall_assessment"] = diagnosis
    explanation["probability_ckd"] = probabilities[1]  # Probability of CKD

    # --- Rule-Based Risk Factor Analysis (Requires Medical Expertise) ---
    significant_factors: List[str] = []
    input_dict: Dict[str, Union[float, int, str]] = input_data.to_dict('records')[0]  # Convert DataFrame row to dictionary

    if input_dict['age_yrs'] and input_dict['age_yrs'] > 60:
        significant_factors.append(f"Elevated age ({input_dict['age_yrs']} years)")
    if input_dict['blood_pressure_mm_hg'] and input_dict['blood_pressure_mm_hg'] > 140:
        significant_factors.append(f"Elevated blood pressure ({input_dict['blood_pressure_mm_hg']} mm/Hg)")
    if input_dict['albumin'] and input_dict['albumin'] > 3.5:  # Example threshold - REPLACE WITH ACCURATE VALUE
        significant_factors.append(f"Elevated albumin ({input_dict['albumin']})")
    if input_dict['sugar'] and input_dict['sugar'] > 2:  # Example threshold - REPLACE WITH ACCURATE VALUE
        significant_factors.append(f"Elevated sugar level ({input_dict['sugar']})")
    if input_dict['serum_creatinine_mgs_dl'] and input_dict['serum_creatinine_mgs_dl'] > 1.2:  # Example
        significant_factors.append(f"Elevated serum creatinine ({input_dict['serum_creatinine_mgs_dl']} mg/dL)")
    if input_dict['hemoglobin_gms'] and input_dict['hemoglobin_gms'] < 10:  # Example
        significant_factors.append(f"Low hemoglobin level ({input_dict['hemoglobin_gms']} gms)")
    if input_dict['hypertension_yes'] == 1:
        significant_factors.append("History of hypertension")
    if input_dict['diabetes_mellitus_yes'] == 1:
        significant_factors.append("History of diabetes mellitus")

    # Add more medically accurate rules here, considering combinations of factors and severity levels!

    if significant_factors:
        explanation["significant_risk_factors"] = {
            "message": "Significant risk factors identified:",
            "factors": significant_factors
        }
    else:
        explanation["significant_risk_factors"] = {"message": "No significant risk factors identified based on the model's criteria."}

    explanation["disclaimer"] = "This is a prediction, not a definitive diagnosis. Consult a healthcare professional for accurate diagnosis and treatment."

    return {"diagnosis": diagnosis, "explanation": explanation}


def predict_ckd(data, model, scaler, feature_names):
    """
    Predict Chronic Kidney Disease (CKD) status.
    """
    logging.info(f"Received data: {data}")  # Log the received data.
    if model is None or scaler is None or feature_names is None:
        logging.error("CKD model, scaler, or feature names are not loaded.")
        return jsonify({"error": "CKD model or scaler is not available"}), 500

    try:
        # 1. Input Validation
        if not isinstance(data, dict):
            logging.error("Invalid input: Input data must be a dictionary.")
            return jsonify({"error": "Invalid input: Input data must be a dictionary."}), 400

        try:
            # Validate the input data using the Pydantic model
            validated_data = CKDData.model_validate(data)
            logging.info(f"Validated CKD input data: {validated_data.model_dump()}")
        except ValidationError as e:
            logging.error(f"Pydantic validation error: {e}")
            return jsonify({"error": f"Invalid input data: {e.errors()}"}), 400

        # 2. Data Conversion and Preprocessing
        input_data = pd.DataFrame([validated_data.model_dump()])
        input_data = input_data[feature_names].fillna(0)  # Ensure correct order of columns and handle missing values

        # 3. Scale the input data
        try:
            input_scaled = scaler.transform(input_data)
        except ValueError as e:
            logging.error(f"Scaling error: {e}")
            return jsonify({"error": "Scaling error"}), 500

        # 4. Model Prediction
        try:
            prediction = model.predict(input_scaled)[0]
            probabilities = model.predict_proba(input_scaled)[0].tolist()
        except Exception as e:
            logging.error(f"Model prediction error: {e}")
            return jsonify({"error": "Model prediction error"}), 500

        # 5. Response Formatting
        response = {
            "prediction": int(prediction),
            "probabilities": probabilities,
            "class_names": ["No CKD", "CKD"],
        }

        # 6. Generate Diagnosis and Explanation
        diagnosis_response = generate_diagnosis_message(prediction, probabilities, feature_names, input_data)

        response.update(diagnosis_response)  # Merge diagnosis and explanation into the response

        logging.info(f"CKD Prediction: {response}")
        return jsonify(response), 200

    except Exception as e:
        logging.error(f"Error processing CKD request: {e}", exc_info=True)
        return jsonify({"error": "An internal error occurred"}), 500