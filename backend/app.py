import logging
from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
import os
import joblib
import tensorflow as tf
import pandas as pd
import psycopg2
from sklearn.preprocessing import LabelEncoder, StandardScaler
from pydantic import BaseModel, Field, confloat, conint, ValidationError  # Keep these imports
from typing import Any, List, Dict, Union, Optional  # Correctly import Optional from typing
from utils.db_utils import get_db_connection, create_encounter, DatabaseError
from patient_encounter_routes import patient_encounter_bp



# Import the prediction functions from the separate files
from malaria_prediction import predict_malaria
from ckd_prediction import predict_ckd
from heart_disease_prediction import predict_heart_disease
from hepatitis_c_prediction import predict_hepatitis_c
from routes.image_processing import image_bp

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Register the blueprints
app.register_blueprint(image_bp, url_prefix="/api/image-processing")
app.register_blueprint(patient_encounter_bp)  # Register patient/encounter routes

# Base model directory (relative to the backend directory)
BASE_MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")

# Model Paths (Use relative paths for cloud deployment like Render)
HEPATITIS_C_MODEL_PATH = os.path.join(BASE_MODEL_DIR, "hepatitis_c_model", "hepatitis_c_model.keras")
CKD_MODEL_PATH = os.path.join(BASE_MODEL_DIR, "ckd_model", "ckd_model.pkl")
CKD_SCALER_PATH = os.path.join(BASE_MODEL_DIR, "ckd_model", "ckd_scaler.pkl")
CKD_FEATURE_NAMES_PATH = os.path.join(BASE_MODEL_DIR, "ckd_model", "ckd_feature_names.pkl")
HEART_DISEASE_MODEL_PATH = os.path.join(BASE_MODEL_DIR, "heart_disease_model", "heart_disease_model.h5")

# Configure logging (Keep this as it is)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load Models (Keep this as it is)
try:
    logging.info("Attempting to load models...")
    hepatitis_c_model = tf.keras.models.load_model(HEPATITIS_C_MODEL_PATH)
    logging.info(f"Hepatitis C model loaded from: {HEPATITIS_C_MODEL_PATH}")
    ckd_model = joblib.load(CKD_MODEL_PATH)
    logging.info(f"CKD model loaded from: {CKD_MODEL_PATH}")
    ckd_scaler = joblib.load(CKD_SCALER_PATH)
    logging.info(f"CKD scaler loaded from: {CKD_SCALER_PATH}")
    with open(CKD_FEATURE_NAMES_PATH, 'rb') as f:
        ckd_feature_names = joblib.load(f)
    logging.info(f"CKD feature names loaded from: {CKD_FEATURE_NAMES_PATH}")
    heart_disease_model = tf.keras.models.load_model(HEART_DISEASE_MODEL_PATH)
    logging.info(f"Heart disease model loaded from: {HEART_DISEASE_MODEL_PATH}")
    logging.info("Models loaded successfully.")
except FileNotFoundError as e:
    logging.error(f"Model file not found: {e}")
    hepatitis_c_model = None
    ckd_model = None
    ckd_scaler = None
    ckd_feature_names = None
    heart_disease_model = None
except Exception as e:
    logging.error(f"Error loading model: {e}", exc_info=True)
    logging.error(f"Exception details: {e}", exc_info=True)
    hepatitis_c_model = None
    ckd_model = None
    ckd_scaler = None
    ckd_feature_names = None
    heart_disease_model = None

# Feature Names (Keep these as they are)
heart_disease_model_feature_names = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal"]
hepatitis_c_model_feature_names = ['Age', 'Sex', 'ALB', 'ALP', 'ALT', 'AST', 'BIL', 'CHE', 'CHOL', 'CREA', 'GGT', 'PROT', 'AST/ALT', 'AgeGroup_Middle', 'AgeGroup_Old']
ckd_feature_names = [
    "Age (yrs)",
    "Blood Pressure (mm/Hg)",
    "Specific Gravity",
    "Albumin",
    "Sugar",
    "Blood Glucose Random (mgs/dL)",
    "Blood Urea (mgs/dL)",
    "Serum Creatinine (mgs/dL)",
    "Sodium (mEq/L)",
    "Potassium (mEq/L)",
    "Hemoglobin (gms)",
    "Packed Cell Volume",
    "White Blood Cells (cells/cmm)",
    "Red Blood Cells (millions/cmm)",
    "Red Blood Cells: normal",
    "Pus Cells: normal",
    "Pus Cell Clumps: present",
    "Bacteria: present",
    "Hypertension: yes",
    "Diabetes Mellitus: yes",
    "Coronary Artery Disease: yes",
    "Appetite: poor",
    "Pedal Edema: yes",
    "Anemia: yes",
]

# Models Dictionary (Keep this as it is)
models = {
    "malaria": None,
    "ckd": ckd_model,
    "heart_disease": heart_disease_model,
    "hepatitis_c": hepatitis_c_model,
}

# Scalers (If Needed) (Keep this as it is)
scalers = {
    "ckd": ckd_scaler
}


# Pydantic models for data validation (Keep these as they are)
class HeartDiseaseData(BaseModel):
    age: float = Field(..., alias="age")
    sex: float = Field(..., alias="sex")
    cp: float = Field(..., alias="cp")
    trestbps: float = Field(..., alias="trestbps")
    chol: float = Field(..., alias="chol")
    fbs: float = Field(..., alias="fbs")
    restecg: float = Field(..., alias="restecg")
    thalach: float = Field(..., alias="thalach")
    exang: float = Field(..., alias="exang")
    oldpeak: float = Field(..., alias="oldpeak")
    slope: float = Field(..., alias="slope")
    ca: float = Field(..., alias="ca")
    thal: float = Field(..., alias="thal")


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


def predict_ckd(data: Dict, model, scaler, feature_names: List[str]):
    """
    Predict Chronic Kidney Disease (CKD) status and provide a detailed explanation.

    Args:
        data (Dict): The input data as a dictionary.
        model: The trained CKD prediction model.
        scaler: The scaler used to scale the input data.
        feature_names (List[str]): The list of feature names.

    Returns:
        jsonify: A JSON response containing the prediction, probabilities,
                and a detailed explanation.
    """
    logging.info(f"CKD - Received data: {data}")

    if model is None or scaler is None or feature_names is None:
        logging.error("CKD model, scaler, or feature names are not loaded.")
        return jsonify({"error": "CKD model or scaler is not available"}), 500

    try:
        # 1. Input Validation
        if not isinstance(data, dict):
            logging.error("CKD - Invalid input: Input data must be a dictionary.")
            return jsonify({"error": "Invalid input: Input data must be a dictionary."}), 400

        try:
            # Validate the input data using the Pydantic model
            validated_data = CKDData.model_validate(data)
            logging.info(f"CKD - Validated data: {validated_data}")
        except ValidationError as e:
            logging.error(f"CKD - Pydantic validation error: {e}")
            return jsonify({"error": f"Invalid input data: {e.errors()}"}), 400  # Return detailed errors

        # 2. Data Conversion and Preprocessing
        input_data = pd.DataFrame([validated_data.model_dump(exclude_none=True)])  # Use validated_data and exclude None

        # Ensure all required features are present and in the correct order
        input_data = input_data.reindex(columns=feature_names, fill_value=0)

        # 3. Scale the input data
        try:
            input_scaled = scaler.transform(input_data)
        except ValueError as e:
            logging.error(f"CKD - Scaling error: {e}")
            return jsonify({"error": "Scaling error"}), 500

        # 4. Model Prediction
        try:
            prediction = model.predict(input_scaled)[0]
            probabilities = model.predict_proba(input_scaled)[0].tolist()
        except Exception as e:
            logging.error(f"CKD - Model prediction error: {e}")
            return jsonify({"error": "Model prediction error"}), 500

        # 5. Generate Detailed Explanation
        explanation = get_ckd_explanation(input_data, probabilities, feature_names, prediction)

        # 6. Response Formatting
        response_data: Dict[str, Union[int, List[float], str, Dict[str, Union[str, float]]]] = {
            "prediction": int(prediction),
            "probabilities": probabilities,
            "class_names": ["No CKD", "CKD"],
            "diagnosis": explanation["diagnosis"],
            "explanation": explanation
        }
        logging.info(f"CKD - Prediction: {response_data}")
        return jsonify(response_data), 200

    except Exception as e:
        logging.error(f"CKD - Error processing request: {e}", exc_info=True)
        return jsonify({"error": "An internal error occurred"}), 500


def get_ckd_explanation(input_data: pd.DataFrame, probabilities: List[float], feature_names: List[str], prediction: int) -> Dict[str, Union[str, Dict[str, Union[str, float]]]]:
    """
    Provides a detailed, rule-based explanation of the CKD prediction.

    Args:
        input_data (pd.DataFrame): The input data used for prediction.
        probabilities (List[float]): The probabilities for each class.
        feature_names (List[str]): The names of the input features.
        prediction (int): The model's prediction (0 or 1).

    Returns:
        Dict[str, Union[str, Dict[str, float]]]: A dictionary containing the diagnosis and explanation.
    """

    explanation: Dict[str, Union[str, Dict[str, Union[str, float]]]] = {}

    if prediction == 1:
        explanation["diagnosis"] = "High likelihood of Chronic Kidney Disease (CKD) detected. Further evaluation is strongly recommended."
    else:
        explanation["diagnosis"] = "Low likelihood of Chronic Kidney Disease (CKD) detected."

    explanation["probability_ckd"] = probabilities[1]  # Probability of CKD

    # --- Rule-Based Risk Factor Analysis (Requires Medical Expertise) ---
    significant_factors: Dict[str, Union[str, float]] = {}
    input_dict: Dict[str, Union[float, int, str]] = input_data.to_dict('records')[0]  # Access the first row as a dict

    if input_dict.get("age_yrs") and input_dict["age_yrs"] > 60:
        significant_factors["Age"] = f"Elevated age ({input_dict['age_yrs']} years)"
    if input_dict.get("blood_pressure_mm_hg") and input_dict["blood_pressure_mm_hg"] > 140:
        significant_factors["Blood Pressure"] = f"Elevated blood pressure ({input_dict['blood_pressure_mm_hg']} mm/Hg)"
    if input_dict.get("albumin") and (input_dict["albumin"] > 3.0 or input_dict["albumin"] < 3.5):  # Example: Outside normal range
        significant_factors["Albumin"] = f"Abnormal albumin level ({input_dict['albumin']})"
    if input_dict.get("sugar") and input_dict["sugar"] > 2:
        significant_factors["Sugar"] = f"Elevated sugar level ({input_dict['sugar']})"
    if input_dict.get("serum_creatinine_mgs_dl") and input_dict["serum_creatinine_mgs_dl"] > 1.2:
        significant_factors["Serum Creatinine"] = f"Elevated serum creatinine ({input_dict['serum_creatinine_mgs_dl']} mg/dL)"
    if input_dict.get("hemoglobin_gms") and input_dict["hemoglobin_gms"] < 10:
        significant_factors["Hemoglobin"] = f"Low hemoglobin level ({input_dict['hemoglobin_gms']} gms)"
    if input_dict.get("hypertension_yes") == 1:
        significant_factors["Hypertension"] = "History of hypertension"
    if input_dict.get("diabetes_mellitus_yes") == 1:
        significant_factors["Diabetes Mellitus"] = "History of diabetes mellitus"
    if input_dict.get("anemia_yes") == 1:
        significant_factors["Anemia"] = "Presence of anemia"

    # Add more medically accurate rules here, considering combinations of factors and severity!

    # Example: Combining multiple risk factors for a more severe assessment
    if input_dict.get("age_yrs") and input_dict["age_yrs"] > 60 and input_dict.get("blood_pressure_mm_hg") and input_dict["blood_pressure_mm_hg"] > 160 and prediction == 1:
        explanation["severity_assessment"] = "Advanced age and high blood pressure significantly increase CKD risk, indicating a potentially severe condition."
    elif prediction == 1:
        explanation["severity_assessment"] = "CKD detected. Further evaluation is recommended to determine severity."
    else:
        explanation["severity_assessment"] = "Low likelihood of CKD. Regular monitoring is advised."

    if significant_factors:
        explanation["significant_risk_factors"] = {
            "message": "Significant risk factors identified:",
            "factors": significant_factors
        }
    else:
        explanation["significant_risk_factors"] = {"message": "No significant risk factors identified based on the model's criteria."}

    explanation["disclaimer"] = "This is a prediction, not a definitive diagnosis. Consult a healthcare professional for accurate diagnosis and treatment."

    return explanation


def predict_heart_disease(models, feature_names):
    """
    Predicts heart disease.
    """
    logging.info("Predicting Heart Disease")

    if models["heart_disease"] is None:
        logging.error("Heart Disease model not loaded.")
        return jsonify({"error": "Heart Disease model not available"}), 500

    try:
        raw_json = request.get_json(force=True)
        logging.info(f"Heart Disease - Received JSON: {raw_json}")

        try:
            validated_data = HeartDiseaseData.model_validate(raw_json)
            logging.info(f"Heart Disease - Validated data: {validated_data}")
        except ValidationError as e:
            logging.error(f"Heart Disease - Pydantic validation error: {e}")
            return jsonify({"error": f"Invalid input data: {e.errors()}"}), 400

        input_data = pd.DataFrame([validated_data.model_dump()])
        input_data = input_data.reindex(columns=feature_names).fillna(0)

        prediction = models["heart_disease"].predict(input_data)[0][0]
        logging.info(f"Heart Disease - Prediction: {prediction}")

        diagnosis_message = "Heart Disease Detected. Please consult a doctor for further evaluation." if prediction > 0.5 else "No Heart Disease Detected."
        return jsonify({"prediction": float(prediction), "diagnosis": diagnosis_message}), 200

    except Exception as e:
        logging.error(f"Heart Disease - Error processing request: {e}", exc_info=True)
        return jsonify({"error": "An internal error occurred"}), 500


@app.route('/api/predict/<disease>', methods=['POST'])
def predict(disease):
    logging.info(f"Predicting {disease}")
    logging.info(f"Models dictionary: {models}")  # Log the models dictionary

    if disease not in models or models[disease] is None:
        logging.error(f"Disease model not found or failed to load: {disease}")
        logging.error(f"Disease: {disease}")  # Log the disease being predicted
        return jsonify({"error": "Disease model not found or failed to load"}), 404

    try:
        raw_json = request.get_json(force=True)  # force=True to handle Content-Type issues
        if not raw_json:
            logging.error("No JSON input provided")
            return jsonify({"error": "No JSON input provided"}), 400

        if disease == "malaria":
            return predict_malaria(models, None)

        elif disease == "ckd":
            return predict_ckd(raw_json, models["ckd"], scalers["ckd"], ckd_feature_names)

        elif disease == "heart_disease":
            logging.info("Calling predict_heart_disease function")
            logging.info(f"Heart Disease Model: {models['heart_disease']}")
            return predict_heart_disease(models, heart_disease_model_feature_names)

        elif disease == "hepatitis_c":
            return predict_hepatitis_c(models, hepatitis_c_model_feature_names)

        return jsonify({"error": "Unhandled disease type"}), 400
    except Exception as e:
        logging.error(f"Error processing request for {disease}: {e}", exc_info=True)
        logging.error(f"Exception details: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run()
    
