import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pandas as pd
from pydantic import BaseModel, Field, ValidationError, conint, confloat
from typing import List, Union, Optional
import re
import requests
import tempfile
import shutil
import joblib

# --- Define PROJECT_ROOT explicitly for app.py ---
# This assumes app.py is in 'backend' folder, and project root is one level up
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# --- Import db and migrate from your extensions.py ---
from extensions import db, migrate

# Load environment variables early
from dotenv import load_dotenv
load_dotenv()

# --- Configure Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# --- Import prediction modules ---
from prediction.malaria_prediction import predict_malaria
from prediction.ckd_prediction import predict_ckd
from prediction.heart_disease_prediction import EnhancedHeartDiseaseDiagnosticSystem
from prediction.hepatitis_c_prediction import predict_hepatitis_c

# --- Import MODEL_URLS from model_config.py ---
from model_config import MODEL_URLS

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# --- Flask-SQLAlchemy Configuration ---
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
        logger.error(f"Environment variable {var} is not set. Please check your .env file or environment configuration.")
        # Consider exiting or raising an error if essential DB vars are missing

app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
db.init_app(app)
migrate.init_app(app, db)
logger.info("Flask-SQLAlchemy and Flask-Migrate initialized.")

# Import your models AFTER db is initialized
from models import Patient, Encounter, Record

from errors import DatabaseError, PatientNotFoundError, EncounterNotFoundError, RecordNotFoundError

# Register blueprints
from patient_encounter_routes import patient_encounter_bp
app.register_blueprint(patient_encounter_bp)

# --- Image processing blueprint modification note ---
# Assuming your routes/image_processing.py has a blueprint named image_bp.
# Ensure that within that blueprint, you validate 'file' in request.files,
# return 400 if missing, and handle image reading/processing safely.
from routes.image_processing import image_bp
app.register_blueprint(image_bp, url_prefix="/api/image-processing")

# Initialize the Heart Disease Diagnostic System globally
heart_disease_diagnoser = EnhancedHeartDiseaseDiagnosticSystem()

# --- Global dictionary to hold all loaded models and auxiliary data ---
loaded_models = {}

# --- Helper functions for downloading and loading models from URLs ---
def download_file(url, local_path):
    """Downloads a file from a given URL to a local path."""
    logger.info(f"Attempting to download {url} to {local_path}")
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
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

def load_single_model_file(model_name: str, url: str, temp_dir: str):
    """Downloads and loads a single model file (e.g., .pkl) from a URL."""
    file_name = os.path.basename(url)
    local_file_path = os.path.join(temp_dir, file_name)

    if not download_file(url, local_file_path):
        logger.error(f"Could not download {model_name} from {url}.")
        return None

    try:
        # Determine how to load based on file extension or known type
        if file_name.endswith('.pkl'):
            model = joblib.load(local_file_path)
            logger.info(f"Successfully loaded {model_name} from {local_file_path}")
            return model
        # Add other file types (e.g., .h5 for Keras/TF, .bin for fastText) here if needed
        else:
            logger.error(f"Unsupported file type for {model_name}: {file_name}. Only .pkl is supported for now.")
            return None
    except Exception as e:
        logger.error(f"Error loading {model_name} from {local_file_path}: {e}")
        return None

def initialize_all_models():
    """Initializes all models and auxiliary data from their configured URLs."""
    global loaded_models
    temp_dir = None
    try:
        # Create a temporary directory for downloaded models
        temp_dir = tempfile.mkdtemp()
        logger.info(f"Created temporary directory for models: {temp_dir}")

        for model_key, model_url in MODEL_URLS.items():
            logger.info(f"Initializing {model_key} from {model_url}...")
            # For simplicity, assuming all are single .pkl files for SymScan related assets
            loaded_obj = load_single_model_file(model_key, model_url, temp_dir)
            if loaded_obj is not None:
                loaded_models[model_key] = loaded_obj
            else:
                logger.error(f"Failed to load {model_key}. Its functionality may be impaired.")

        if not loaded_models:
            logger.error("No models were loaded. Check MODEL_URLS and network connectivity.")

    except Exception as e:
        logger.critical(f"Fatal error during model initialization: {e}")
        # Clear loaded models if initialization fails critically
        loaded_models = {}
    finally:
        # Clean up the temporary directory after loading
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up temporary directory: {temp_dir}")
            except OSError as e:
                logger.warning(f"Error removing temporary directory {temp_dir}: {e}")

# Load models at app context start
with app.app_context():
    initialize_all_models()

# --- NLTK Setup: Add BOTH backend/nltk_data and backend/venv/nltk_data to NLTK_DATA path ---
import nltk

backend_dir = os.path.dirname(__file__)

# Path 1: backend/nltk_data
project_nltk_data = os.path.join(backend_dir, 'nltk_data')
# Path 2: backend/venv/nltk_data
venv_nltk_data = os.path.join(backend_dir, 'venv', 'nltk_data')

for p in [project_nltk_data, venv_nltk_data]:
    if p not in nltk.data.path:
        nltk.data.path.insert(0, p)

# Log the paths being used
logger.info(f"NLTK data search paths: {nltk.data.path}")

# Validate required corpora
try:
    nltk.data.find('corpora/wordnet')
    nltk.data.find('corpora/omw-1.4')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('tokenizers/punkt')
    logger.info("✅ All required NLTK data found.")
except LookupError as e:
    logger.error(
        f"❌ Missing required NLTK data: {e}\n"
        f"👉 Run `python setup_env.py` to download them into both locations."
    )
    # This might cause issues if NLTK functions are called later without the data
    # Consider raising an error or marking NLTK-dependent features as unavailable

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# SYMPTOM_SYNONYMS dictionary removed as requested

def clean_text_api(text):
    if pd.isna(text):
        return None
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def lemmatize_and_remove_stopwords_api(text: str):
    tokens = nltk.word_tokenize(text)
    tokens = [lemmatizer.lemmatize(t) for t in tokens if t not in stop_words]
    return ' '.join(tokens)

def normalize_symptom_name_api(symptom_name):
    if not symptom_name:
        return None
    cleaned = clean_text_api(symptom_name.replace('_', ' '))
    if not cleaned:
        return None
    # Removed: return SYMPTOM_SYNONYMS.get(lemmatized, lemmatized)
    return lemmatize_and_remove_stopwords_api(cleaned) 

# --- =================  --- #
#===== Pydantic models ======#

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
    # Corrected: Expect 'age' (lowercase) to match the frontend
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

# SymScan config
MIN_CONFIDENCE_THRESHOLD = 0.50
TOP_N_PREDICTIONS = 3

@app.route('/api/predict/<disease>', methods=['POST'])
def predict(disease):
    logger.info(f"Received prediction request for disease: {disease}")
    try:
        raw_json = request.get_json()
        if not raw_json:
            logger.error("No JSON input provided for prediction.")
            return jsonify({"error": "No JSON input provided", "medical_disclaimer": "This system is informational only and not a substitute for professional medical advice."}), 400

        if disease == "malaria":
            try:
                # If predict_malaria expects a dict, pass raw_json, but ideally, it should be validated.
                prediction_results = predict_malaria(raw_json)
                return jsonify(prediction_results)
            except Exception as e:
                logger.exception(f"Error in Malaria prediction: {e}")
                return jsonify({"error": "Internal error during Malaria prediction.", "details": str(e), "medical_disclaimer": "This system is informational only and not a substitute for professional medical advice."}), 500

        elif disease == "ckd":
            try:
                validated_data = CKDData(**raw_json).model_dump(by_alias=True)
                prediction_results = predict_ckd(validated_data)
                return jsonify(prediction_results)
            except ValidationError as e:
                logger.error(f"CKD validation error: {e.errors()}")
                return jsonify({"error": "Invalid input format for CKD", "details": e.errors(), "medical_disclaimer": "This system is informational only and not a substitute for professional medical advice."}), 400
            except Exception as e:
                logger.exception(f"Error in CKD prediction: {e}")
                return jsonify({"error": "Internal error during CKD prediction.", "details": str(e), "medical_disclaimer": "This system is informational only and not a substitute for professional medical advice."}), 500

        elif disease == "heart_disease":
            try:
                # Pydantic will now correctly expect 'age' (lowercase)
                validated_numerical_data = HeartDiseaseData(**raw_json).model_dump() # .model_dump() by default uses field names
                logger.info(f"Starting hybrid prediction for patient data: {validated_numerical_data}")

                # Ensure the prediction function converts custom objects (like RiskLevel) to strings
                result = heart_disease_diagnoser.predict_with_hybrid_approach(validated_numerical_data)

                # Ensure result is JSON serializable, especially if RiskLevel was used
                if "risk_level" in result and hasattr(result["risk_level"], 'value'):
                    result["risk_level"] = result["risk_level"].value # Convert enum to string

                if "error" in result:
                    logger.error(f"Heart Disease prediction error: {result['details']}")
                    return jsonify(result), 400
                return jsonify(result)
            except ValidationError as e:
                logger.error(f"Heart Disease validation error: {e.errors()}")
                return jsonify({"error": "Invalid input format for Heart Disease", "details": e.errors(), "medical_disclaimer": "This system is informational only and not a substitute for professional medical advice."}), 400
            except Exception as e:
                logger.exception(f"Error in Heart Disease prediction: {e}")
                return jsonify({"error": "Internal error during Heart Disease prediction.", "details": str(e), "medical_disclaimer": "This system is informational only and not a substitute for professional medical advice."}), 500

        elif disease == "hepatitis_c":
            try:
                validated_data = HepatitisCData(**raw_json).model_dump(by_alias=True)
                prediction_results = predict_hepatitis_c(validated_data)
                return jsonify(prediction_results)
            except ValidationError as e:
                logger.error(f"Hepatitis C validation error: {e.errors()}")
                return jsonify({"error": "Invalid input format for Hepatitis C", "details": e.errors(), "medical_disclaimer": "This system is informational only and not a substitute for professional medical advice."}), 400
            except Exception as e:
                logger.exception(f"Error in Hepatitis C prediction: {e}")
                return jsonify({"error": "Internal error during Hepatitis C prediction.", "details": str(e), "medical_disclaimer": "This system is informational only and not a substitute for professional medical advice."}), 500

        elif disease == "symscan":
            try:
                # Retrieve models and data from the global loaded_models dictionary
                symscan_classifier = loaded_models.get("symScan_sympton_classifier_model")
                symscan_unique_symptoms = loaded_models.get("symScan_unique_symptoms")
                # symscan_unique_diseases is not directly used for the column names or mapping, but can be useful
                # symscan_unique_diseases = loaded_models.get("symScan_unique_diseases")
                symscan_int_to_disease = loaded_models.get("symScan_int_to_disease_map")
                symscan_precautions_map = loaded_models.get("symScan_precautions_map")

                # Check if models are loaded before proceeding
                if None in [symscan_classifier, symscan_unique_symptoms, symscan_int_to_disease, symscan_precautions_map]:
                    logger.error("SymScan model or auxiliary data not loaded. Returning 503.")
                    return jsonify({
                        "error": "SymScan model not available. Please contact support or try again later.",
                        "medical_disclaimer": "This system is informational only and not a substitute for professional medical advice."
                    }), 503

                symscan_input = SymScanData(**raw_json)
                user_symptoms_raw = symscan_input.symptoms

                logger.info(f"SymScan: Received raw symptoms: {user_symptoms_raw}")

                normalized_user_symptoms_used = set()
                unrecognized_symptoms_list = []

                for sym_raw in user_symptoms_raw:
                    normalized_sym = normalize_symptom_name_api(sym_raw)
                    if normalized_sym:
                        if normalized_sym in symscan_unique_symptoms:
                            normalized_user_symptoms_used.add(normalized_sym)
                        else:
                            unrecognized_symptoms_list.append(f"'{sym_raw}' (normalized to '{normalized_sym}' but not in model vocabulary)")
                            logger.warning(f"SymScan: Symptom '{sym_raw}' normalized to '{normalized_sym}' not in training vocabulary.")
                    else:
                        unrecognized_symptoms_list.append(f"'{sym_raw}' (could not be normalized)")
                        logger.warning(f"SymScan: Could not normalize symptom: '{sym_raw}'")

                if not normalized_user_symptoms_used:
                    return jsonify({
                        "error": "No recognizable symptoms provided after normalization. Please provide valid symptoms.",
                        "provided_symptoms": user_symptoms_raw,
                        "unrecognized_symptoms": unrecognized_symptoms_list,
                        "medical_disclaimer": "This system is informational only and not a substitute for professional medical advice."
                    }), 400

                logger.info(f"SymScan: Normalized symptoms used for prediction: {normalized_user_symptoms_used}")

                input_vector = [1 if symptom in normalized_user_symptoms_used else 0 for symptom in symscan_unique_symptoms]
                input_df = pd.DataFrame([input_vector], columns=symscan_unique_symptoms)

                prediction_label_int = symscan_classifier.predict(input_df)[0]
                primary_predicted_disease = symscan_int_to_disease.get(prediction_label_int, "Unknown Disease")

                prediction_proba_array = None
                try:
                    prediction_proba_array = symscan_classifier.predict_proba(input_df)[0]
                except AttributeError:
                    logger.warning("SymScan classifier missing predict_proba, confidence unavailable.")

                primary_confidence = prediction_proba_array[prediction_label_int] if prediction_proba_array is not None else None

                if primary_confidence is not None and primary_confidence < MIN_CONFIDENCE_THRESHOLD:
                    primary_predicted_disease = "Uncertain Diagnosis"
                    logger.info(f"SymScan: Primary prediction confidence {primary_confidence:.4f} below threshold {MIN_CONFIDENCE_THRESHOLD}.")

                top_predictions = []
                if prediction_proba_array is not None:
                    # Get indices of top N predictions
                    # Assuming symscan_unique_diseases list from model_config.py or directly from int_to_disease map keys
                    # For correct ordering, it's crucial that symscan_int_to_disease maps to the correct indices
                    all_diseases_sorted_by_index = [symscan_int_to_disease[i] for i in sorted(symscan_int_to_disease.keys())]

                    if all_diseases_sorted_by_index and len(prediction_proba_array) == len(all_diseases_sorted_by_index):
                        # Create a list of (confidence, index) pairs, sort, and take top N
                        sorted_predictions = sorted(
                            [(prob, i) for i, prob in enumerate(prediction_proba_array)],
                            key=lambda item: item[0], reverse=True
                        )[:TOP_N_PREDICTIONS]

                        for conf, idx in sorted_predictions:
                            disease_name = symscan_int_to_disease.get(idx, "Unknown Disease")
                            top_predictions.append({
                                "disease": disease_name,
                                "confidence": f"{conf:.4f}"
                            })
                    else:
                        logger.warning("SymScan: Cannot determine top N predictions, unique diseases list mismatch or missing.")
                elif primary_predicted_disease != "Uncertain Diagnosis":
                    top_predictions.append({
                        "disease": primary_predicted_disease,
                        "confidence": "N/A"
                    })

                if primary_predicted_disease != "Uncertain Diagnosis":
                    precautions = symscan_precautions_map.get(primary_predicted_disease, ["No specific precautions found for this disease."])
                else:
                    precautions = ["Diagnosis is uncertain. It is highly recommended to consult a medical professional for a proper diagnosis and treatment plan."]

                response_data = {
                    "predicted_disease": primary_predicted_disease,
                    "confidence_for_primary_prediction": f"{primary_confidence:.4f}" if primary_confidence is not None else "N/A",
                    "top_n_predictions": top_predictions,
                    "precautions": precautions,
                    "provided_raw_symptoms": user_symptoms_raw,
                    "normalized_symptoms_used_by_model": sorted(list(normalized_user_symptoms_used)),
                    "unrecognized_symptoms": unrecognized_symptoms_list,
                    "medical_disclaimer": "This system is informational only and not a substitute for professional medical advice."
                }

                logger.info(f"SymScan prediction response: {response_data}")
                return jsonify(response_data)

            except ValidationError as e:
                logger.error(f"SymScan input validation error: {e.errors()}")
                return jsonify({
                    "error": "Invalid input format for SymScan prediction",
                    "details": e.errors(),
                    "medical_disclaimer": "This system is informational only and not a substitute for professional medical advice."
                }), 400
            except Exception as e:
                logger.exception(f"SymScan prediction error: {e}")
                return jsonify({
                    "error": "Internal error during SymScan prediction",
                    "details": str(e),
                    "medical_disclaimer": "This system is informational only and not a substitute for professional medical advice."
                }), 500

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