import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pandas as pd
from pydantic import BaseModel, Field, ValidationError, conint, confloat
from typing import List, Union, Optional, Dict, Any
import re
import requests
import tempfile
import shutil
import joblib
import tensorflow as tf
import numpy as np
from io import BytesIO

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

from extensions import db, migrate
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from prediction.malaria_prediction import predict_malaria
from prediction.ckd_prediction import predict_ckd
from prediction.heart_disease_prediction import predict_heart_disease
from prediction.hepatitis_c_prediction import predict_hepatitis_c
from prediction.sysscan_prediction import predict_symscan

from model_config import MODEL_URLS
from services.image_processing_service import process_image as process_malaria_image_data

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

db_name = os.environ.get("DB_NAME")
db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")
db_host = os.environ.get("DB_HOST")
db_port = os.environ.get("DB_PORT", "5432")

required_env_vars = {
    "DB_NAME": db_name,
    "DB_USER": db_user,
    "DB_PASSWORD": db_password,
    "DB_HOST": db_host,
}

for var, value in required_env_vars.items():
    if value is None:
        logger.error(f"Environment variable {var} is not set.")

app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate.init_app(app, db)
logger.info("Flask-SQLAlchemy and Flask-Migrate initialized.")

from models import Patient, Encounter, Record

from errors import DatabaseError, PatientNotFoundError, EncounterNotFoundError, RecordNotFoundError

from patient_encounter_routes import patient_encounter_bp
app.register_blueprint(patient_encounter_bp)

loaded_models: Dict[str, Any] = {}

def download_and_load_joblib(url: str) -> Any:
    """Fetches a joblib artifact from a URL and loads it directly into memory."""
    try:
        logger.info(f"Fetching joblib artifact from {url}")
        response = requests.get(url)
        response.raise_for_status()
        return joblib.load(BytesIO(response.content))
    except Exception as e:
        logger.error(f"Failed to load artifact from {url}: {e}")
        return None

def download_and_load_tensorflow(url: str, temp_dir: str) -> Optional[tf.keras.Model]:
    """Downloads a TensorFlow model from a URL and loads it from a temporary path."""
    temp_path = os.path.join(temp_dir, os.path.basename(url))
    if not download_file(url, temp_path):
        return None
    
    try:
        model = tf.keras.models.load_model(temp_path)
        return model
    except Exception as e:
        logger.error(f"Error loading TensorFlow model from {temp_path}: {e}")
        return None
    
def download_file(url, local_path):
    """Downloads a file from a given URL to a local path."""
    logger.info(f"Attempting to download {url} to {local_path}")
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        logger.info(f"Successfully downloaded {url}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download {url}: {e}")
        return False
    except IOError as e:
        logger.error(f"Failed to write file {local_path}: {e}")
        return False

def initialize_all_models():
    """Initializes all models and auxiliary data from their configured URLs."""
    global loaded_models
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp()
        logger.info(f"Created temporary directory for models: {temp_dir}")

        for model_key, model_url in MODEL_URLS.items():
            if model_url.endswith(('.pkl', '.joblib')):
                loaded_obj = download_and_load_joblib(model_url)
            elif model_url.endswith(('.h5', '.keras', '.tflite')):
                loaded_obj = download_and_load_tensorflow(model_url, temp_dir)
            else:
                logger.warning(f"Unsupported file extension for model {model_key}. Skipping.")
                continue

            if loaded_obj is not None:
                loaded_models[model_key] = loaded_obj
                logger.info(f"Successfully loaded {model_key}.")
            else:
                logger.error(f"Failed to load {model_key}. Functionality may be impaired.")

        if not loaded_models:
            logger.error("No models were loaded. Check MODEL_URLS and network connectivity.")

    except Exception as e:
        logger.critical(f"Fatal error during model initialization: {e}")
        loaded_models = {}
    finally:
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up temporary directory: {temp_dir}")
            except OSError as e:
                logger.warning(f"Error removing temporary directory {temp_dir}: {e}")

with app.app_context():
    initialize_all_models()

import nltk

backend_dir = os.path.dirname(__file__)
project_nltk_data = os.path.join(backend_dir, 'nltk_data')
venv_nltk_data = os.path.join(backend_dir, 'venv', 'nltk_data')

for p in [project_nltk_data, venv_nltk_data]:
    if p not in nltk.data.path:
        nltk.data.path.insert(0, p)

logger.info(f"NLTK data search paths: {nltk.data.path}")

try:
    nltk.data.find('corpora/wordnet')
    nltk.data.find('corpora/omw-1.4')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('tokenizers/punkt')
    logger.info("✅ All required NLTK data found.")
except LookupError as e:
    logger.error(f"❌ Missing required NLTK data: {e}\n"
                 f"👉 Run `python setup_env.py` to download them into both locations.")

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))


class HepatitisCData(BaseModel):
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

class HeartDiseaseData(BaseModel):
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

class SymScanData(BaseModel):
    symptoms: List[str] = Field(..., min_length=1, description="List of symptoms.")


@app.route('/api/image-processing/process-image', methods=['POST'])
def process_malaria_image():
    """
    Endpoint for processing an uploaded image for malaria diagnosis.
    This route calls the dedicated malaria prediction logic.
    """
    try:
        response, status_code = predict_malaria(
            models=loaded_models,
            process_image=process_malaria_image_data
        )
        return response, status_code

    except Exception as e:
        logger.exception(f"Unhandled error in image processing endpoint: {e}")
        return jsonify({
            "error": "Internal server error.",
            "details": str(e),
            "medical_disclaimer": "This system is informational only and not a substitute for professional medical advice."
        }), 500

@app.route('/api/predict/<disease>', methods=['POST'])
def predict(disease: str):
    logger.info(f"Received prediction request for disease: {disease}")
    try:
        raw_json = request.get_json()
        if not raw_json:
            logger.error("No JSON input provided for prediction.")
            return jsonify({"error": "No JSON input provided", "medical_disclaimer": "This system is informational only and not a substitute for professional medical advice."}), 400

        if disease == "heart_disease":
            try:
                validated_numerical_data = HeartDiseaseData(**raw_json).model_dump()
                
                heart_disease_models = {
                    'rf_model': loaded_models.get('heart_disease_rf_model'),
                    'scaler': loaded_models.get('heart_disease_scaler'),
                    'feature_names': loaded_models.get('heart_disease_feature_names')
                }

                if not all(heart_disease_models.values()):
                     logger.error("Heart Disease model artifacts not loaded. Returning 503.")
                     return jsonify({"error": "Heart Disease model not available.", "medical_disclaimer": "..."}), 503

                result = predict_heart_disease(validated_numerical_data, heart_disease_models)
                return jsonify(result)
            except ValidationError as e:
                logger.error(f"Heart Disease validation error: {e.errors()}")
                return jsonify({"error": "Invalid input format for Heart Disease", "details": e.errors(), "medical_disclaimer": "..."}), 400
            except Exception as e:
                logger.exception(f"Error in Heart Disease prediction: {e}")
                return jsonify({"error": "Internal error during Heart Disease prediction.", "details": str(e), "medical_disclaimer": "..."}), 500

        elif disease == "symscan":
            try:
                validated_data = SymScanData(**raw_json).model_dump()
                user_symptoms = validated_data.get('symptoms')
                
                symscan_models = {
                    'symscan_model': loaded_models.get('symscan_sympton_classifier_model'),
                    'unique_symptoms': loaded_models.get('symscan_unique_symptoms'),
                    'int_to_disease_map': loaded_models.get('symscan_int_to_disease_map'),
                    'precautions_map': loaded_models.get('symscan_precautions_map')
                }
                
                if not all(symscan_models.values()):
                     logger.error("SymScan model artifacts not loaded. Returning 503.")
                     return jsonify({"error": "SymScan model not available.", "medical_disclaimer": "..."}), 503
                     
                result = predict_symscan(user_symptoms, symscan_models)
                return jsonify(result)
            except ValidationError as e:
                logger.error(f"SymScan validation error: {e.errors()}")
                return jsonify({"error": "Invalid input format for SymScan prediction", "details": e.errors(), "medical_disclaimer": "..."}), 400
            except Exception as e:
                logger.exception(f"SymScan prediction error: {e}")
                return jsonify({"error": "Internal error during SymScan prediction", "details": str(e), "medical_disclaimer": "..."}), 500

        elif disease == "ckd":
            try:
                validated_data = CKDData(**raw_json).model_dump(by_alias=True)
                prediction_results = predict_ckd(validated_data, loaded_models)
                return jsonify(prediction_results)
            except ValidationError as e:
                logger.error(f"CKD validation error: {e.errors()}")
                return jsonify({"error": "Invalid input format for CKD", "details": e.errors(), "medical_disclaimer": "..."}), 400
            except Exception as e:
                logger.exception(f"Error in CKD prediction: {e}")
                return jsonify({"error": "Internal error during CKD prediction.", "details": str(e), "medical_disclaimer": "..."}), 500

        elif disease == "hepatitis_c":
            try:
                validated_data = HepatitisCData(**raw_json).model_dump(by_alias=True)
                prediction_results = predict_hepatitis_c(validated_data, loaded_models)
                return jsonify(prediction_results)
            except ValidationError as e:
                logger.error(f"Hepatitis C validation error: {e.errors()}")
                return jsonify({"error": "Invalid input format for Hepatitis C", "details": e.errors(), "medical_disclaimer": "..."}), 400
            except Exception as e:
                logger.exception(f"Error in Hepatitis C prediction: {e}")
                return jsonify({"error": "Internal error during Hepatitis C prediction.", "details": str(e), "medical_disclaimer": "..."}), 500

        else:
            logger.warning(f"Unsupported disease type requested: {disease}")
            return jsonify({
                "error": f"Prediction for disease '{disease}' is not supported.",
                "medical_disclaimer": "This system is informational only and not a substitute for professional medical advice."
            }), 400

    except Exception as e:
        logger.exception(f"Unhandled error for disease {disease}: {e}")
        return jsonify({
            "error": "Internal server error during prediction. Please try again later.",
            "medical_disclaimer": "This system is informational only and not a substitute for professional medical advice."
        }), 500

@app.route('/')
def hello():
    return "Welcome to the Multi-Disease Diagnosis System API!"

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)