import os
import joblib
import numpy as np
import pandas as pd
import logging
from typing import Dict, Union, List, Tuple
from dataclasses import dataclass
from enum import Enum
from io import BytesIO
import tempfile
import json
import requests # Import requests library

# Try to import TensorFlow, provide helpful error if not installed
try:
    # We still need these for type hints, but we won't use them to load the model
    from tensorflow.keras.models import load_model as keras_load_model
    from tensorflow import keras
    _tensorflow_available = True
except ImportError:
    _tensorflow_available = False
    print("Warning: TensorFlow not found. ML model predictions will be skipped.")

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
# Environment variables for AWS S3 URLs of Heart Disease model artifacts
HEART_DISEASE_MODEL_URL = os.getenv("HEART_DISEASE_MODEL_URL", "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/heart_disease_model_advanced/heart_disease_model_advanced.keras")
HEART_DISEASE_SCALER_URL = os.getenv("HEART_DISEASE_SCALER_URL", "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/heart_disease_model_advanced/heart_disease_scaler.pkl")
HEART_DISEASE_POLY_FEATURES_URL = os.getenv("HEART_DISEASE_POLY_FEATURES_URL", "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/heart_disease_model_advanced/heart_disease_polynomial_features.pkl")
HEART_DISEASE_PCA_URL = os.getenv("HEART_DISEASE_PCA_URL", "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/heart_disease_model_advanced/heart_disease_pca.pkl")
HEART_DISEASE_FEATURE_NAMES_URL = os.getenv("HEART_DISEASE_FEATURE_NAMES_URL", "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/heart_disease_model_advanced/heart_disease_feature_names.pkl")

# Global instances (will be populated on startup)
heart_disease_model_instance = None
heart_disease_scaler_instance = None
heart_disease_polynomial_features_instance = None
heart_disease_pca_instance = None
heart_disease_feature_names_list = None

from io import BytesIO
import joblib
import requests

def load_joblib_from_url(url: str):
    """Fetches a joblib artifact from a URL and loads it into memory."""
    if not url:
        raise ValueError("URL is not set.")
    try:
        logger.info(f"Fetching artifact from {url}")
        response = requests.get(url)
        response.raise_for_status()
        return joblib.load(BytesIO(response.content))
    except Exception as e:
        logger.error(f"Failed to load artifact from {url}: {e}")
        raise RuntimeError(f"Failed to load model artifact from URL: {url}") from e

def load_heart_disease_artifacts():
    """
    Loads pre-trained ML model artifacts directly from URLs into memory.
    This version skips Keras model loading due to file system dependency.
    """
    global heart_disease_model_instance, heart_disease_scaler_instance, \
        heart_disease_polynomial_features_instance, heart_disease_pca_instance, \
        heart_disease_feature_names_list

    try:
        # Load joblib artifacts from URLs
        heart_disease_scaler_instance = load_joblib_from_url(HEART_DISEASE_SCALER_URL)
        heart_disease_polynomial_features_instance = load_joblib_from_url(HEART_DISEASE_POLY_FEATURES_URL)
        heart_disease_pca_instance = load_joblib_from_url(HEART_DISEASE_PCA_URL)
        heart_disease_feature_names_list = load_joblib_from_url(HEART_DISEASE_FEATURE_NAMES_URL)
        
        # We explicitly skip the Keras model, as it cannot be loaded without a local file path
        if _tensorflow_available:
            logger.warning("TensorFlow is available, but the Keras model is not being loaded "
                           "because it requires a local file path. The model must be served "
                           "via an external service or loaded differently.")
            heart_disease_model_instance = None
        else:
            logger.warning("TensorFlow not available. Keras model loading skipped.")

        logger.info("Heart Disease joblib artifacts loaded successfully from URLs. Keras model was skipped.")

    except Exception as e:
        logger.error(f"Failed to load Heart Disease ML artifacts from URLs: {e}", exc_info=True)
        heart_disease_model_instance = None
        heart_disease_scaler_instance = None
        heart_disease_polynomial_features_instance = None
        heart_disease_pca_instance = None
        heart_disease_feature_names_list = None
        raise RuntimeError("Application startup failed due to missing or corrupt model artifacts.") from e

# Load artifacts once on module import/app startup
load_heart_disease_artifacts()

# --- Risk Level Enum ---
class RiskLevel(Enum):
    VERY_LOW = "Very Low Risk"
    LOW = "Low Risk"
    MODERATE = "Moderate Risk"
    HIGH = "High Risk"
    CRITICAL = "Critical Risk"
    INDETERMINATE = "Indeterminate Risk (Conflicting Data)"

# --- Knowledge Base Data Structures ---
@dataclass
class MedicalRule:
    condition: str
    risk_score: float
    evidence_weight: float
    description: str
    recommendation: str

@dataclass
class DiagnosticEvidence:
    factor: str
    value: Union[int, float, str]
    risk_contribution: float
    confidence: float
    reasoning: str

# --- Medical Knowledge Base ---
class HeartDiseaseKnowledgeBase:
    def __init__(self):
        self.rules = self._initialize_medical_rules()
        self.risk_factors = self._initialize_risk_factors()
        self.normal_ranges = self._initialize_normal_ranges()
        self.feature_mapping = self._initialize_feature_mapping()
        
    def _initialize_medical_rules(self) -> List[MedicalRule]:
        """
        Initialize comprehensive medical rules based on cardiology guidelines.
        These rules provide a basis for the rule-based component of the hybrid system.
        """
        return [
            # Critical Risk Rules - designed to flag severe conditions immediately
            MedicalRule(
                condition="major_vessels_severe",
                risk_score=0.98,
                evidence_weight=0.95,
                description="Severe multi-vessel coronary artery disease (>=3 vessels affected)",
                recommendation="URGENT: Immediate cardiology consultation for revascularization"
            ),
            MedicalRule(
                condition="thalassemia_fixed_defect",
                risk_score=0.95,
                evidence_weight=0.90,
                description="Fixed perfusion defect indicating myocardial infarction (scar tissue)",
                recommendation="URGENT: Immediate evaluation for previous MI and current risk"
            ),
            MedicalRule(
                condition="st_depression_extreme",
                risk_score=0.92,
                evidence_weight=0.88,
                description="Extreme ST depression (e.g., > 2.5mm) during exercise suggests severe ischemia",
                recommendation="URGENT: Stress test highly indicative of severe CAD. Expedite cardiology consult."
            ),
            MedicalRule(
                condition="max_hr_critically_low_with_symptoms",
                risk_score=0.90,
                evidence_weight=0.85,
                description="Critically low maximum heart rate during exercise, especially with symptoms, indicates severe cardiac dysfunction.",
                recommendation="EMERGENCY: Immediate medical evaluation, potential cardiac arrest risk."
            ),
            MedicalRule(
                condition="resting_bp_critically_low_with_symptoms",
                risk_score=0.90,
                evidence_weight=0.85,
                description="Critically low resting blood pressure, especially with symptoms, indicates severe circulatory shock.",
                recommendation="EMERGENCY: Immediate medical evaluation, potential for hemodynamic collapse."
            ),
            
            # High Risk Rules - indicate significant risk requiring prompt attention
            MedicalRule(
                condition="chest_pain_typical_angina",
                risk_score=0.85,
                evidence_weight=0.80,
                description="Typical angina pattern strongly suggests coronary artery disease (CAD)",
                recommendation="Immediate stress testing and cardiology referral"
            ),
            MedicalRule(
                condition="exercise_angina_positive",
                risk_score=0.80,
                evidence_weight=0.75,
                description="Exercise-induced angina indicates significant coronary stenosis",
                recommendation="Stress testing and possible cardiac catheterization"
            ),
            MedicalRule(
                condition="st_slope_downsloping",
                risk_score=0.78,
                evidence_weight=0.75,
                description="Downsloping ST segment during exercise is a strong indicator of myocardial ischemia.",
                recommendation="Cardiology evaluation for coronary artery disease"
            ),
            MedicalRule(
                condition="multiple_major_risk_factors",
                risk_score=0.70,
                evidence_weight=0.65,
                description="Presence of multiple major cardiovascular risk factors (e.g., age, high cholesterol, diabetes, hypertension)",
                recommendation="Comprehensive cardiovascular risk assessment and aggressive risk factor modification"
            ),
            
            # Moderate Risk Rules - suggest a need for intervention and monitoring
            MedicalRule(
                condition="cholesterol_very_high",
                risk_score=0.60,
                evidence_weight=0.55,
                description="Very high cholesterol levels (e.g., >240 mg/dL)",
                recommendation="Lipid management and cardiovascular risk assessment"
            ),
            MedicalRule(
                condition="hypertension_severe",
                risk_score=0.55,
                evidence_weight=0.50,
                description="Severe hypertension (e.g., Resting BP > 160/100 mmHg)",
                recommendation="Blood pressure management and cardiac evaluation"
            ),
            MedicalRule(
                condition="diabetes_uncontrolled",
                risk_score=0.50,
                evidence_weight=0.45,
                description="Uncontrolled diabetes mellitus (e.g., high Fasting BS)",
                recommendation="Glycemic control and cardiovascular screening"
            )
        ]
    
    def _initialize_risk_factors(self) -> Dict[str, Dict]:
        """
        Initialize risk factor scoring system based on clinical significance.
        Each factor has 'ranges' (for continuous values) or specific 'values' (for categorical),
        along with a 'weight' indicating its overall importance in the rule-based system.
        """
        return {
            'age': {
                'ranges': [(0, 40, 0.1), (40, 55, 0.3), (55, 65, 0.5), (65, 75, 0.7), (75, 100, 0.9)],
                'weight': 0.15
            },
            'sex': {
                'male': 0.6, 'female': 0.4,
                'weight': 0.10
            },
            'cp': {
                'typical angina': 0.9, 'atypical angina': 0.6, 
                'non-anginal pain': 0.3, 'asymptomatic': 0.1,
                'weight': 0.20
            },
            'trestbps': {
                'ranges': [(0, 120, 0.1), (120, 130, 0.3), (130, 140, 0.5), (140, 160, 0.7), (160, 250, 0.9)],
                'weight': 0.15
            },
            'chol': {
                'ranges': [(0, 200, 0.2), (200, 240, 0.4), (240, 300, 0.7), (300, 500, 0.9)],
                'weight': 0.15
            },
            'fbs': {
                'normal': 0.2, 'elevated': 0.8,
                'weight': 0.10
            },
            'restecg': {
                'normal': 0.1, 'st-t abnormality': 0.5, 'left ventricular hypertrophy': 0.6,
                'weight': 0.05
            },
            'thalach': {
                'ranges': [(0, 100, 0.8), (100, 140, 0.5), (140, 180, 0.2), (180, 220, 0.1)],
                'weight': 0.10
            },
            'exang': {
                'no': 0.1, 'yes': 0.8,
                'weight': 0.15
            },
            'oldpeak': {
                'ranges': [(0, 1.0, 0.1), (1.0, 2.0, 0.4), (2.0, 3.0, 0.7), (3.0, 7.0, 0.9)],
                'weight': 0.20
            },
            'slope': {
                'upsloping': 0.2, 'flat': 0.5, 'downsloping': 0.8,
                'weight': 0.18
            },
            'ca': {
                'ranges': [(0, 1, 0.1), (1, 2, 0.4), (2, 3, 0.7), (3, 4, 0.95)],
                'weight': 0.25
            },
            'thal': {
                'normal': 0.1, 'reversible defect': 0.5, 'fixed defect': 0.9,
                'weight': 0.22
            }
        }
    
    def _initialize_normal_ranges(self) -> Dict[str, Tuple[float, float]]:
        """Define normal physiological ranges for various parameters, used for input validation."""
        return {
            'age': (18, 100),
            'trestbps': (70, 200),
            'chol': (100, 400),
            'thalach': (60, 220),
            'oldpeak': (0.0, 5.0),
            'ca': (0, 3),
            'fbs': (0, 1)
        }

    def _initialize_feature_mapping(self) -> Dict[str, Dict]:
        """Maps user-friendly input names to ML feature names and their numerical encodings."""
        return {
            "Age (years)": {"ml_name": "age"},
            "Sex": {"ml_name": "sex", "mapping": {"Male": 1, "Female": 0}},
            "Chest Pain Type": {"ml_name": "cp", "mapping": {"Typical Angina": 0, "Atypical Angina": 1, "Non-anginal Pain": 2, "Asymptomatic": 3}},
            "Resting BP (mm Hg)": {"ml_name": "trestbps"},
            "Cholesterol (mg/dL)": {"ml_name": "chol"},
            "Fasting BS > 120 mg/dL": {"ml_name": "fbs", "mapping": {"Yes": 1, "No": 0}},
            "Resting ECG": {"ml_name": "restecg", "mapping": {"Normal": 0, "ST-T wave abnormality": 1, "Left Ventricular Hypertrophy": 2}},
            "Max Heart Rate (bpm)": {"ml_name": "thalach"},
            "Exercise Induced Angina": {"ml_name": "exang", "mapping": {"Yes": 1, "No": 0}},
            "ST Depression (mm)": {"ml_name": "oldpeak"},
            "ST Segment Slope": {"ml_name": "slope", "mapping": {"Upsloping": 0, "Flat": 1, "Downsloping": 2}},
            "Major Vessels (fluoroscopy)": {"ml_name": "ca"},
            "Thalassemia": {"ml_name": "thal", "mapping": {"Normal": 1, "Fixed Defect": 2, "Reversible Defect": 3}}
        }

# --- Rule-Based System ---
class RuleBasedDiagnosticSystem:
    def __init__(self, knowledge_base: HeartDiseaseKnowledgeBase):
        self.kb = knowledge_base
        
    def evaluate_critical_rules(self, patient_data: Dict) -> Tuple[bool, List[str], float, bool]:
        """
        Evaluates patient data against predefined critical rules.
        These rules can override ML predictions if a severe condition is met.
        Returns (is_critical_override, critical_reasons, critical_risk_score, is_contradictory).
        """
        critical_flags = []
        max_risk_score = 0.0
        is_contradictory = False
        
        # Access data using ML feature names for consistency
        age = patient_data.get('age')
        cp = patient_data.get('cp')
        thalach = patient_data.get('thalach')
        exang = patient_data.get('exang')
        trestbps = patient_data.get('trestbps')
        oldpeak = patient_data.get('oldpeak')
        slope = patient_data.get('slope')
        ca = patient_data.get('ca')
        thal = patient_data.get('thal')

        # Rule 1: Severe multi-vessel disease (ca >= 3)
        if ca is not None and ca >= 3:
            critical_flags.append("Severe multi-vessel coronary artery disease")
            max_risk_score = max(max_risk_score, self.kb.rules[0].risk_score)
            logger.debug(f"Critical Rule Triggered: Severe multi-vessel disease (ca={ca})")
            
        # Rule 2: Fixed perfusion defect (Thalassemia == 2)
        if thal is not None and thal == 2:
            critical_flags.append("Fixed perfusion defect (previous MI)")
            max_risk_score = max(max_risk_score, self.kb.rules[1].risk_score)
            logger.debug(f"Critical Rule Triggered: Fixed perfusion defect (thal={thal})")

        # Rule 3: Extreme ST Depression during exercise (oldpeak > 2.5)
        if oldpeak is not None and oldpeak > 2.5:
            critical_flags.append("Extreme ST depression during exercise")
            max_risk_score = max(max_risk_score, self.kb.rules[2].risk_score)
            logger.debug(f"Critical Rule Triggered: Extreme ST depression (oldpeak={oldpeak})")

        # Rule 4: Critically low Max HR with symptoms (example thresholds)
        if thalach is not None and thalach < 70 and (cp == 0 or exang == 1):
            critical_flags.append("Critically low Max Heart Rate with cardiac symptoms")
            max_risk_score = max(max_risk_score, self.kb.rules[3].risk_score)
            logger.debug(f"Critical Rule Triggered: Critically low Max HR (thalach={thalach}, cp={cp}, exang={exang})")

        # Rule 5: Critically low Resting BP (example threshold)
        if trestbps is not None and trestbps < 70:
            critical_flags.append("Critically low Resting Blood Pressure")
            max_risk_score = max(max_risk_score, self.kb.rules[4].risk_score)
            logger.debug(f"Critical Rule Triggered: Critically low BP (trestbps={trestbps})")
            
        # --- Contradiction Detection ---
        if (slope is not None and slope == 2 and
            ca is not None and ca == 0 and
            thal is not None and thal == 1):
            
            is_contradictory = True
            critical_flags.append("Conflicting results: Downsloping ST with no major vessel disease and normal perfusion scan. Requires careful clinical review.")
            max_risk_score = 0.5
            logger.warning(f"Contradiction Detected: Downsloping ST ({slope}) with CA=0 ({ca}) and Normal Thal ({thal}). Risk adjusted to {max_risk_score}.")

        return len(critical_flags) > 0, critical_flags, max_risk_score, is_contradictory
    
    def calculate_risk_score(self, patient_data: Dict) -> Tuple[float, List[DiagnosticEvidence]]:
        """
        Calculate a comprehensive risk score for the patient based on rule-based logic
        and the predefined risk factors in the knowledge base.
        """
        evidence_list = []
        total_weighted_score = 0.0
        total_weight = 0.0
        
        # Evaluate each risk factor defined in the knowledge base
        for factor_ml_name, config in self.kb.risk_factors.items():
            evidence = self._evaluate_risk_factor(factor_ml_name, patient_data, config)
            if evidence:
                evidence_list.append(evidence)
                if 'weight' in config:
                    total_weighted_score += evidence.risk_contribution * config['weight']
                    total_weight += config['weight']
                else:
                    logger.warning(f"Weight not found for factor '{factor_ml_name}'. Skipping its contribution to total_weighted_score.")
        
        final_risk_score = total_weighted_score / total_weight if total_weight > 0 else 0.0
        logger.debug(f"Rule-based final risk score: {final_risk_score:.2f}")
        logger.debug(f"Rule-based evidence collected: {evidence_list}")
        
        return final_risk_score, evidence_list
    
    def _evaluate_risk_factor(self, factor_ml_name: str, patient_data: Dict, config: Dict) -> Union[DiagnosticEvidence, None]:
        """
        Evaluates an individual risk factor from the patient's data against
        the knowledge base configuration.
        """
        try:
            value = patient_data.get(factor_ml_name)
            if value is None:
                logger.debug(f"Skipping evaluation for missing factor: {factor_ml_name}")
                return None
            
            risk_score = 0.0
            reasoning = ""
            display_value = value

            if 'ranges' in config:
                risk_score = self._evaluate_ranges(value, config['ranges'])
                reasoning = f"{factor_ml_name} {value} contributes {risk_score:.2f} risk"
            elif isinstance(config, dict):
                # Reverse map numerical ML value to string for rule lookup and reasoning
                if factor_ml_name == 'sex':
                    display_value = 'Male' if value == 1 else 'Female'
                    risk_score = config.get(display_value.lower(), 0.0)
                elif factor_ml_name == 'cp':
                    cp_map_back = {0: 'typical angina', 1: 'atypical angina', 2: 'non-anginal pain', 3: 'asymptomatic'}
                    display_value = cp_map_back.get(value, 'unknown')
                    risk_score = config.get(display_value, 0.0)
                elif factor_ml_name == 'fbs':
                    display_value = 'elevated' if value == 1 else 'normal'
                    risk_score = config.get(display_value, 0.0)
                elif factor_ml_name == 'exang':
                    display_value = 'yes' if value == 1 else 'no'
                    risk_score = config.get(display_value, 0.0)
                elif factor_ml_name == 'restecg':
                    restecg_map_back = {0: 'normal', 1: 'st-t abnormality', 2: 'left ventricular hypertrophy'}
                    display_value = restecg_map_back.get(value, 'unknown')
                    risk_score = config.get(display_value, 0.0)
                elif factor_ml_name == 'slope':
                    slope_map_back = {0: 'upsloping', 1: 'flat', 2: 'downsloping'}
                    display_value = slope_map_back.get(value, 'unknown')
                    risk_score = config.get(display_value, 0.0)
                elif factor_ml_name == 'thal':
                    thal_map_back = {1: 'normal', 2: 'fixed defect', 3: 'reversible defect'}
                    display_value = thal_map_back.get(value, 'unknown')
                    risk_score = config.get(display_value, 0.0)
                else:
                    logger.warning(f"Unknown categorical factor: {factor_ml_name}")
                    return None
                
            reasoning = f"{factor_ml_name} '{display_value}' contributes {risk_score:.2f} risk"
            
            logger.debug(f"    Evaluating {factor_ml_name}: {display_value}, Risk: {risk_score:.2f}")
            return DiagnosticEvidence(
                factor=factor_ml_name.replace('_', ' ').title(),
                value=display_value,
                risk_contribution=risk_score,
                confidence=config.get('confidence', 0.8),
                reasoning=reasoning
            )
        except Exception as e:
            logger.warning(f"Error evaluating {factor_ml_name}: {e}", exc_info=True)
            return None
    
    def _evaluate_ranges(self, value: float, ranges: List[Tuple]) -> float:
        """Evaluates a numerical value against defined ranges to determine its risk contribution."""
        for min_val, max_val, risk_score in ranges:
            if min_val <= value < max_val:
                return risk_score
        if ranges:
            return ranges[-1][2]
        return 0.0

# Global artifact instances
heart_disease_model_instance = None
heart_disease_scaler_instance = None
heart_disease_polynomial_features_instance = None
heart_disease_pca_instance = None
heart_disease_feature_names_list = None



def preprocess_user_input_for_ml(raw_data: Dict, kb: HeartDiseaseKnowledgeBase) -> Tuple[pd.DataFrame, str]:
    processed_data = {}
    validation_messages = []
    
    # Create a mapping from ml_name back to user_key for error messages
    ml_to_user = {v['ml_name']: k for k, v in kb.feature_mapping.items()}
    
    for ml_key in kb.risk_factors.keys():
        user_key = ml_to_user.get(ml_key, ml_key)
        user_value = raw_data.get(ml_key) or raw_data.get(user_key)
        
        if user_value is None or user_value == "":
            if ml_key in ['age', 'trestbps', 'chol', 'thalach', 'oldpeak', 'cp', 'sex', 'fbs', 'exang', 'slope', 'ca', 'thal']:
                raise ValueError(f"Missing critical input: '{user_key}'. Please provide this value.")
            else:
                processed_data[ml_key] = 0.0
                continue
        
        # Find the config for this field
        config = None
        for uk, cfg in kb.feature_mapping.items():
            if cfg['ml_name'] == ml_key:
                config = cfg
                user_key = uk
                break
        
        if config is None:
            raise ValueError(f"Internal error: No configuration found for field '{ml_key}'")
        
        if "mapping" in config:
            # Handle numeric values for categorical fields
            if isinstance(user_value, (int, float)):
                # For sex: 1 -> Male, 0 -> Female
                if ml_key == 'sex':
                    mapped_value = int(user_value)
                    display_value = 'Male' if mapped_value == 1 else 'Female'
                # For other categorical fields, use the numeric value directly
                else:
                    mapped_value = int(user_value)
                    display_value = str(mapped_value)
            else:
                # Handle string inputs
                mapped_value = config["mapping"].get(str(user_value))
                display_value = str(user_value)
            
            if mapped_value is None:
                raise ValueError(f"Invalid value for '{user_key}': '{display_value}'. Expected one of {list(config['mapping'].keys())} or appropriate numeric values.")
            
            processed_data[ml_key] = float(mapped_value)
        else:
            # Numerical value processing
            try:
                numeric_value = float(user_value)
                processed_data[ml_key] = numeric_value
            except ValueError:
                raise ValueError(f"Invalid numerical input for '{user_key}': '{user_value}'. Must be a number.")
        
        # Physiological validation
        normal_range = kb.normal_ranges.get(ml_key)
        if normal_range and ml_key in processed_data:
            value_to_check = processed_data[ml_key]
            min_val, max_val = normal_range
            if not (min_val <= value_to_check <= max_val):
                msg = f"'{user_key}' ({value_to_check}) is outside the normal physiological range ({min_val}-{max_val})."
                validation_messages.append(msg)
                logger.warning(f"Validation Warning: {msg}")
                if ml_key in ['trestbps', 'thalach'] and (value_to_check < 40 or value_to_check > 250):
                    raise ValueError(f"Critical out-of-range value for '{user_key}': {value_to_check}. This value is physiologically implausible.")
    
    if heart_disease_feature_names_list is None:
        raise RuntimeError("ML feature names are not loaded. Cannot preprocess data.")

    df = pd.DataFrame([processed_data])
    df = df.reindex(columns=heart_disease_feature_names_list, fill_value=0.0)
    
    # Rest of your preprocessing code...
    return final_processed_data, combined_validation_message


def _predict_heart_disease_ml_only(processed_data: pd.DataFrame) -> Dict:
    """
    Performs the Machine Learning prediction for Heart Disease using the loaded model.
    This function expects already preprocessed numerical data that matches the ML model's expected features.
    """
    if not _tensorflow_available:
        return {
            "prediction": "N/A",
            "probability": "N/A",
            "ml_status": "Skipped",
            "details": "TensorFlow not installed. ML prediction skipped."
        }

    # Ensure artifacts are loaded before prediction (redundant if load_heart_disease_artifacts is called globally but good for safety)
    load_heart_disease_artifacts() 

    if heart_disease_model_instance is None:
        logger.error("Heart Disease ML model is not loaded. Cannot perform prediction.")
        return {"prediction": "N/A", "probability": "N/A", "ml_status": "Failed", "details": "Heart Disease ML model not available."}

    try:
        # Convert DataFrame to numpy array if not already
        input_array = processed_data.values
        
        # The model expects a batch, so add an extra dimension if it's a single sample
        if input_array.ndim == 1:
            input_array = np.expand_dims(input_array, axis=0) # Add batch dimension

        logger.debug(f"Input array shape for ML prediction: {input_array.shape}")
        
        predictions = heart_disease_model_instance.predict(input_array)
        logger.debug(f"Raw ML predictions: {predictions}")

        # For binary classification with sigmoid, predictions[0][0] will be the probability of class 1
        probability_of_disease = float(predictions[0][0])
        prediction_class = 1 if probability_of_disease >= 0.5 else 0

        logger.info(f"Heart Disease ML prediction: Class={prediction_class}, Probability={probability_of_disease:.4f}")

        return {
            "prediction": "Positive" if prediction_class == 1 else "Negative",
            "probability": f"{probability_of_disease:.4f}",
            "ml_status": "Success",
            "details": f"ML model predicted disease with {probability_of_disease:.2%} confidence."
        }

    except Exception as e:
        logger.error(f"Error during Heart Disease ML-only prediction: {e}", exc_info=True)
        return {"prediction": "N/A", "probability": "N/A", "ml_status": "Failed", "details": f"ML prediction failed: {str(e)}"}


# --- Enhanced Hybrid Diagnostic System ---
class EnhancedHeartDiseaseDiagnosticSystem:
    def __init__(self):
        self.kb = HeartDiseaseKnowledgeBase()
        self.rule_based_system = RuleBasedDiagnosticSystem(self.kb)

    def predict_with_hybrid_approach(self, raw_user_data: Dict) -> Dict:
        """
        Combines rule-based logic and ML prediction for a comprehensive heart disease diagnosis.
        
        Args:
            raw_user_data (Dict): Raw patient input received from the API request.
                                   Expected to contain user-friendly keys (e.g., "Age (years)", "Sex").
        
        Returns:
            Dict: A dictionary containing the diagnosis, risk level, explanations, and recommendations.
        """
        logger.info(f"Starting hybrid prediction for patient data: {raw_user_data}")
        
        diagnosis_results = {
            "diagnosis": "Uncertain",
            "risk_level": RiskLevel.INDETERMINATE.value,
            "rule_based_risk_score": 0.0,
            "ml_prediction": "N/A",
            "ml_probability": "N/A",
            "explanations": [],
            "recommendations": [],
            "warnings": [],
            "critical_flags": [],
            "contradiction_detected": False,
            "details": "Processing initiated."
        }

        try:
            # Step 1: Preprocess user input for ML model and perform initial validation
            try:
                processed_ml_data, validation_msg = preprocess_user_input_for_ml(raw_user_data, self.kb)
                if validation_msg != "Input validated successfully.":
                    diagnosis_results["warnings"].append(validation_msg)
                    logger.warning(f"Input validation warnings: {validation_msg}")
            except ValueError as ve:
                diagnosis_results["diagnosis"] = "Input Error"
                diagnosis_results["risk_level"] = RiskLevel.INDETERMINATE.value
                diagnosis_results["details"] = f"Input preprocessing failed: {str(ve)}"
                diagnosis_results["error"] = str(ve)
                logger.error(f"Preprocessing failed: {str(ve)}")
                return diagnosis_results
            except RuntimeError as re:
                diagnosis_results["diagnosis"] = "System Error"
                diagnosis_results["risk_level"] = RiskLevel.INDETERMINATE.value
                diagnosis_results["details"] = f"ML artifact loading error during preprocessing: {str(re)}"
                diagnosis_results["error"] = str(re)
                logger.error(f"ML artifact loading error during preprocessing: {str(re)}")
                return diagnosis_results
            
            # Step 2: Evaluate Critical Rules (Rule-Based System)
            is_critical, critical_reasons, critical_rb_score, is_contradictory = \
                self.rule_based_system.evaluate_critical_rules(processed_ml_data.iloc[0].to_dict()) # Pass dictionary of first row
            
            diagnosis_results["critical_flags"] = critical_reasons
            diagnosis_results["contradiction_detected"] = is_contradictory
            
            if is_critical and not is_contradictory:
                # If a critical rule fires and it's not due to contradiction, override
                diagnosis_results["diagnosis"] = "Critical Risk Detected"
                diagnosis_results["risk_level"] = RiskLevel.CRITICAL.value
                diagnosis_results["explanations"].extend(critical_reasons)
                diagnosis_results["recommendations"].append(self.kb.rules[0].recommendation) # Take a strong recommendation
                diagnosis_results["rule_based_risk_score"] = critical_rb_score
                diagnosis_results["details"] = "Critical condition identified by rule-based system. Immediate action advised."
                logger.warning(f"Critical override applied. Reasons: {critical_reasons}")
                return diagnosis_results # Exit early for critical cases

            # If contradiction detected, set risk to indeterminate and return
            if is_contradictory:
                diagnosis_results["diagnosis"] = "Conflicting Data"
                diagnosis_results["risk_level"] = RiskLevel.INDETERMINATE.value
                diagnosis_results["explanations"].extend(critical_reasons) # Critical reasons now include contradiction
                diagnosis_results["recommendations"].append("Further diagnostic tests and expert clinical review are urgently needed due to conflicting findings.")
                diagnosis_results["rule_based_risk_score"] = critical_rb_score # Contradiction might force a moderate score
                diagnosis_results["details"] = "Conflicting physiological data detected, requiring immediate expert review and additional diagnostics."
                logger.warning(f"Contradiction detected. Details: {critical_reasons}")
                return diagnosis_results # Exit early for contradictory cases

            # Step 3: Get ML Prediction (only if TensorFlow is available and artifacts loaded)
            ml_result = {"prediction": "N/A", "probability": "N/A", "ml_status": "Skipped", "details": "TensorFlow not available."}
            if _tensorflow_available and heart_disease_model_instance is not None:
                ml_result = _predict_heart_disease_ml_only(processed_ml_data)
                diagnosis_results["ml_prediction"] = ml_result.get("prediction", "N/A")
                diagnosis_results["ml_probability"] = ml_result.get("probability", "N/A")
                diagnosis_results["explanations"].append(f"ML Model Prediction: {ml_result.get('prediction')} (Probability: {ml_result.get('probability')})")
                if ml_result.get("ml_status") == "Failed":
                    diagnosis_results["warnings"].append(f"ML prediction failed: {ml_result.get('details')}")
                    logger.error(f"ML prediction failed: {ml_result.get('details')}")
            else:
                diagnosis_results["warnings"].append("ML prediction skipped as TensorFlow/model not available.")
                logger.warning("ML prediction skipped due to missing TensorFlow or model.")

            # Step 4: Calculate Rule-Based Risk Score (if not already overridden)
            rule_based_risk_score, rule_based_evidence = self.rule_based_system.calculate_risk_score(processed_ml_data.iloc[0].to_dict())
            diagnosis_results["rule_based_risk_score"] = rule_based_risk_score
            diagnosis_results["explanations"].append("Rule-Based Risk Factors:")
            for evidence in rule_based_evidence:
                diagnosis_results["explanations"].append(f"- {evidence.factor}: {evidence.reasoning}")

            # Step 5: Combine Scores (Simple Averaging for demonstration, can be more complex)
            # Assign weights, e.g., ML_weight + Rule_weight = 1.0
            ml_weight = 0.6 if _tensorflow_available and heart_disease_model_instance is not None else 0.0
            rule_weight = 1.0 - ml_weight # If ML is not available, rule-based takes full weight

            combined_risk_score = 0.0
            if ml_result.get("prediction") == "Positive" and ml_result.get("probability") != "N/A":
                # Convert probability string to float for calculation
                ml_prob_float = float(ml_result["probability"]) if isinstance(ml_result["probability"], str) else ml_result["probability"]
                # Use the ML probability of positive outcome
                combined_risk_score = (ml_prob_float * ml_weight) + (rule_based_risk_score * rule_weight)
                logger.debug(f"Combined risk score (ML positive): ({ml_prob_float} * {ml_weight}) + ({rule_based_risk_score} * {rule_weight}) = {combined_risk_score:.2f}")
            else:
                # If ML is negative or skipped, rely more on rule-based or a lower ML contribution
                # If ML is negative, its "probability of disease" might be low (e.g., < 0.5)
                ml_prob_float = float(ml_result["probability"]) if isinstance(ml_result["probability"], str) else ml_result["probability"]
                if ml_result.get("prediction") == "Negative" and ml_prob_float != "N/A":
                    # Use (1 - probability of disease) if it's predicting negative, or just consider it low.
                    # For simplicity, if ML is negative, we'll let rule-based be more dominant or cap combined risk.
                    # This logic can be refined based on false negative/positive costs.
                    combined_risk_score = (ml_prob_float * ml_weight) + (rule_based_risk_score * rule_weight) # Still use probability of class 1
                    logger.debug(f"Combined risk score (ML negative/N/A): ({ml_prob_float} * {ml_weight}) + ({rule_based_risk_score} * {rule_weight}) = {combined_risk_score:.2f}")
                else:
                    combined_risk_score = rule_based_risk_score # If ML is not available/failed, rely solely on rules
                    logger.debug(f"Combined risk score (ML unavailable): {rule_based_risk_score:.2f} (Rule-based only)")

            # Step 6: Determine Final Diagnosis and Risk Level
            final_diagnosis = "Negative for Heart Disease"
            final_risk_level = RiskLevel.VERY_LOW.value
            final_recommendation = "Maintain healthy lifestyle, regular check-ups."

            if combined_risk_score >= RiskLevel.CRITICAL.value: # Check against actual enum values if applicable, or define numerical thresholds
                final_risk_level = RiskLevel.CRITICAL.value
                final_diagnosis = "High Probability of Severe Heart Disease"
                final_recommendation = "URGENT: Immediate cardiology consultation and advanced diagnostics."
            elif combined_risk_score >= 0.7:
                final_risk_level = RiskLevel.HIGH.value
                final_diagnosis = "High Probability of Heart Disease"
                final_recommendation = "Prompt cardiology referral, stress test, and lifestyle modification."
            elif combined_risk_score >= 0.5:
                final_risk_level = RiskLevel.MODERATE.value
                final_diagnosis = "Moderate Probability of Heart Disease"
                final_recommendation = "Cardiology evaluation, risk factor management, and regular monitoring."
            elif combined_risk_score >= 0.3:
                final_risk_level = RiskLevel.LOW.value
                final_diagnosis = "Low Probability of Heart Disease"
                final_recommendation = "Continue healthy lifestyle, annual check-ups, monitor symptoms."
            
            diagnosis_results["diagnosis"] = final_diagnosis
            diagnosis_results["risk_level"] = final_risk_level
            diagnosis_results["recommendations"].insert(0, final_recommendation) # Main recommendation first
            diagnosis_results["combined_risk_score"] = f"{combined_risk_score:.4f}"
            diagnosis_results["details"] = "Hybrid diagnosis complete."

        except Exception as e:
            logger.exception(f"An unexpected error occurred during hybrid prediction: {e}")
            diagnosis_results["diagnosis"] = "System Error"
            diagnosis_results["risk_level"] = RiskLevel.INDETERMINATE.value
            diagnosis_results["explanations"].append(f"An unexpected internal error occurred: {str(e)}")
            diagnosis_results["recommendations"].append("Please contact support or try again later.")
            diagnosis_results["error"] = str(e)
            diagnosis_results["details"] = "Prediction failed due to an unhandled exception."

        logger.info(f"Hybrid prediction complete. Result: {diagnosis_results['risk_level']} - {diagnosis_results['diagnosis']}")
        return diagnosis_results