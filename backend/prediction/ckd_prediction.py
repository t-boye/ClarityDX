import logging
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, confloat, conint, ValidationError
from typing import Optional, List, Dict, Union

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# --- Pydantic Data Model ---
# This is used for input validation and remains unchanged.
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
    """
    Generates a user-friendly diagnosis message based on the model's prediction.
    """
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

    # Note: These are general thresholds and may not match the exact model features.
    # You can adjust these based on your model's feature importance.
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

def predict_ckd(data: Dict, models: Dict) -> Dict:
    """
    Performs a CKD prediction using the models loaded in the main application.
    The `models` dictionary is passed from `app.py`.
    """
    logger.info(f"CKD prediction request received.")

    # 1. Retrieve the models from the `models` dictionary
    ckd_model = models.get("ckd_model")
    ckd_scaler = models.get("ckd_scaler")
    ckd_feature_names = models.get("ckd_feature_names")

    # 2. Validate that all necessary components are available
    if None in [ckd_model, ckd_scaler, ckd_feature_names]:
        logger.error("CKD model components not found in loaded_models. Check model_config.py.")
        return {
            "error": "CKD prediction service is unavailable. Required model files are missing.",
            "status_code": 503,
            "medical_disclaimer": "This system is informational only and not a substitute for professional medical advice."
        }

    try:
        # 3. Validate and preprocess the input data
        validated_data = CKDData.model_validate(data).model_dump(by_alias=True)
        input_df = pd.DataFrame([validated_data])

        # Ensure the DataFrame has all the required columns for the model,
        # filling missing values with NaNs to be handled by the scaler.
        input_df = input_df.reindex(columns=ckd_feature_names, fill_value=np.nan)

        # 4. Scale the numerical features using the loaded scaler
        scaled_features = ckd_scaler.transform(input_df)
        scaled_df = pd.DataFrame(scaled_features, columns=ckd_feature_names)

        # 5. Make the prediction
        prediction_label = ckd_model.predict(scaled_df)[0]
        prediction_proba = ckd_model.predict_proba(scaled_df)[0].tolist()

        logger.info(f"CKD Prediction: {prediction_label}, Probabilities: {prediction_proba}")

        # 6. Generate the user-friendly response
        diagnosis_info = generate_ckd_diagnosis_message(
            prediction=prediction_label,
            probabilities=prediction_proba,
            input_data=input_df
        )

        response_payload = {
            "prediction": int(prediction_label),
            "probabilities": prediction_proba,
            "class_names": ["No CKD", "CKD"],
            **diagnosis_info
        }
        
        logger.info(f"CKD prediction successful. Response: {response_payload}")
        return response_payload

    except ValidationError as e:
        logger.error(f"CKD input validation error: {e.errors()}")
        return {
            "error": "Invalid input data format for CKD prediction.",
            "details": e.errors(),
            "status_code": 400,
            "medical_disclaimer": "This system is informational only and not a substitute for professional medical advice."
        }
    except Exception as e:
        logger.exception(f"An unexpected error occurred during CKD prediction: {e}")
        return {
            "error": "An internal server error occurred during CKD prediction.",
            "details": str(e),
            "status_code": 500,
            "medical_disclaimer": "This system is informational only and not a substitute for professional medical advice."
        }