import pandas as pd
import numpy as np
import os
import joblib
import shutil
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
from enum import Enum
from io import BytesIO
import logging
from typing import Dict, Any, Union, List, Optional
import tempfile
import requests

# Try to import TensorFlow, provide helpful error if not installed
try:
    from tensorflow.keras.models import load_model as keras_load_model
    from tensorflow import keras
    _tensorflow_available = True
except ImportError:
    _tensorflow_available = False
    print("Warning: TensorFlow not found. Some ML model predictions will be skipped.")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define the base URL for the Hepatitis C model artifacts
HEPATITIS_C_BASE_URL = "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/hepatitis_c_model/"

# Get environment variables for all remote model artifact URLs, with fallbacks to the S3 paths
HEPATITIS_C_SCALER_URL = os.getenv("HEPATITIS_C_SCALER_URL", f"{HEPATITIS_C_BASE_URL}hepatitis_c_scaler.pkl")
HEPATITIS_C_RF_MODEL_URL = os.getenv("HEPATITIS_C_RF_MODEL_URL", f"{HEPATITIS_C_BASE_URL}random_forest_model.pkl")
HEPATITIS_C_FEATURE_NAMES_URL = os.getenv("HEPATITIS_C_FEATURE_NAMES_URL", f"{HEPATITIS_C_BASE_URL}hepatitis_c_feature_names.pkl")
HEPATITIS_C_TF_MODEL_URL = os.getenv("HEPATITIS_C_TF_MODEL_URL", f"{HEPATITIS_C_BASE_URL}hepatitis_c_model.tf/")

# Global instances
hepatitis_c_scaler = None
hepatitis_c_rf_model = None
hepatitis_c_tf_model = None
hepatitis_c_feature_names = None

def load_joblib_from_url(url: str):
    """
    Fetches a joblib artifact from a URL and loads it directly into memory.
    """
    if not url:
        raise ValueError("URL for joblib artifact is not set.")
    try:
        logger.info(f"Fetching joblib artifact from {url}")
        response = requests.get(url)
        response.raise_for_status()
        return joblib.load(BytesIO(response.content))
    except Exception as e:
        logger.error(f"Failed to load artifact from {url}: {e}")
        raise RuntimeError(f"Failed to load model artifact from URL: {url}") from e

def load_tensorflow_saved_model_from_url(base_url: str):
    """
    Loads a TensorFlow SavedModel from a remote URL. This requires downloading
    the model's directory structure to a temporary location.
    """
    if not base_url:
        raise ValueError("Base URL for TensorFlow SavedModel is not set.")
    
    if not _tensorflow_available:
        raise RuntimeError("TensorFlow not available. Cannot load SavedModel.")

    # Define the list of files to download based on the SavedModel format
    files_to_download = [
        "fingerprint.pb",
        "keras_metadata.pb",
        "saved_model.pb",
        "variables/variables.data-00000-of-00001",
        "variables/variables.index"
    ]
    
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp()
        logger.info(f"Downloading TensorFlow SavedModel to temporary directory: {temp_dir}")
        
        for file_name in files_to_download:
            url = f"{base_url}{file_name}"
            local_path = os.path.join(temp_dir, file_name)
            
            # Create subdirectories if they don't exist
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            logger.info(f"Downloading {url} to {local_path}")
            response = requests.get(url)
            response.raise_for_status()
            with open(local_path, "wb") as f:
                f.write(response.content)
        
        logger.info("All TensorFlow model files downloaded successfully.")
        model = keras_load_model(temp_dir)
        logger.info("TensorFlow SavedModel loaded into memory.")
        return model

    except Exception as e:
        logger.error(f"Failed to load TensorFlow SavedModel from {base_url}: {e}")
        raise RuntimeError(f"Failed to load TensorFlow model from URL: {base_url}") from e
    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            logger.info(f"Removed temporary directory {temp_dir}")

def load_hepatitis_c_artifacts():
    """
    Loads all Hepatitis C model artifacts directly from URLs into memory.
    """
    global hepatitis_c_scaler, hepatitis_c_rf_model, hepatitis_c_tf_model, hepatitis_c_feature_names

    try:
        # Load joblib artifacts
        hepatitis_c_scaler = load_joblib_from_url(HEPATITIS_C_SCALER_URL)
        hepatitis_c_rf_model = load_joblib_from_url(HEPATITIS_C_RF_MODEL_URL)
        hepatitis_c_feature_names = load_joblib_from_url(HEPATITIS_C_FEATURE_NAMES_URL)

        # Load TensorFlow model
        hepatitis_c_tf_model = load_tensorflow_saved_model_from_url(HEPATITIS_C_TF_MODEL_URL)

        logger.info("All Hepatitis C model artifacts loaded successfully from URLs.")
    
    except Exception as e:
        logger.error(f"Failed to load Hepatitis C ML artifacts: {e}", exc_info=True)
        # Reset globals to None if loading fails
        hepatitis_c_scaler = None
        hepatitis_c_rf_model = None
        hepatitis_c_tf_model = None
        hepatitis_c_feature_names = None
        raise RuntimeError("Application startup failed due to missing or corrupt Hepatitis C model artifacts.") from e

# Load artifacts once at import or app startup
try:
    load_hepatitis_c_artifacts()
except RuntimeError as e:
    logger.error(str(e))
    # Note: Global variables remain None as set in the exception handler

# The old 'if artifacts is not None:' block is removed.
# The global variables are now managed directly by the load function.


# You can then create a predict function that uses the loaded objects, for example:
def predict_hepatitis_c(input_data: dict) -> dict:
    # We now check the global variables directly
    if hepatitis_c_tf_model is None or hepatitis_c_scaler is None:
        logger.error("Model artifacts not loaded.")
        return {"error": "Model artifacts not available", "status_code": 500}

    try:
        # preprocess input dict to DataFrame as needed
        input_df = pd.DataFrame([input_data])
        input_scaled = hepatitis_c_scaler.transform(input_df)
        
        # Use the TensorFlow model for prediction
        # The output of the model is likely a single probability, but predict() returns an array
        prediction_proba = hepatitis_c_tf_model.predict(input_scaled)[0][0] 
        # The above line assumes a single output neuron for binary classification
        
        # We need to decide a class based on the probability, e.g., a threshold of 0.5
        prediction = 1 if prediction_proba >= 0.5 else 0
        
        logger.info(f"Prediction: {prediction}, Probabilities: {prediction_proba}")
        
        return {
            "prediction": prediction,
            "probabilities": [1 - prediction_proba, prediction_proba],
            "class_names": ["No Hepatitis C", "Hepatitis C"]
        }
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return {"error": "Prediction failed", "status_code": 500}

# Define feature columns for the ML model (must match training data)
ML_FEATURES = [
    'Age', 'Gender', 'BMI', 'Smoking', 'AlcoholConsumption',
    'PreviousMedicalConditions', 'FamilyHistory', 'ALT', 'AST', 'ALP',
    'Bilirubin', 'Albumin', 'Platelets', 'HCV_RNA_Viral_Load'
]

# Normal/Reference Ranges for LFTs (Approximate values for adults, often vary by lab)
NORMAL_RANGES = {
    'ALT': {'min': 7, 'max': 55},
    'AST': {'min': 8, 'max': 48},
    'ALP': {'min': 40, 'max': 129},
    'Bilirubin': {'min': 0.1, 'max': 1.2},
    'Albumin': {'min': 3.5, 'max': 5.0},
    'Platelets': {'min': 150, 'max': 450}
}

# Define risk level enumeration for clear diagnosis
class RiskLevel(Enum):
    VERY_LOW = "Very Low Risk"
    LOW = "Low Risk"
    MODERATE = "Moderate Risk"
    HIGH = "High Risk"
    CRITICAL = "Critical Risk"

# --- ML Model Management (Simulated for demonstration) ---
# NOTE: The dummy model creation and loading logic is no longer needed
# as we are now loading models from remote URLs.
# I've removed this section to keep the code clean and focused on the
# remote artifact loading strategy. If you need it for local development,
# you would re-add it as a fallback.

# --- Knowledge Base for Rule-Based System ---
class HepatitisCKnowledgeBase:
    def __init__(self, normal_ranges):
        self.normal_ranges = normal_ranges
        logger.info("HepatitisCKnowledgeBase initialized.")

    def is_lft_elevated(self, test: str, value: float) -> bool:
        if test in self.normal_ranges:
            return value > self.normal_ranges[test]['max']
        return False

    def is_lft_low(self, test: str, value: float) -> bool:
        if test in self.normal_ranges:
            return value < self.normal_ranges[test]['min']
        return False

# --- Rule-Based System for General Liver Health Risk ---
class HepatitisCRuleBasedSystem:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        logger.info("HepatitisCRuleBasedSystem initialized.")

    def evaluate_rules(self, patient_data: Dict[str, Any]) -> tuple[float, list[str]]:
        risk_score = 0.0
        evidence = []
        
        alt = patient_data.get('ALT', NORMAL_RANGES['ALT']['min'])
        ast = patient_data.get('AST', NORMAL_RANGES['AST']['min'])
        alp = patient_data.get('ALP', NORMAL_RANGES['ALP']['min'])
        bilirubin = patient_data.get('Bilirubin', NORMAL_RANGES['Bilirubin']['min'])
        albumin = patient_data.get('Albumin', NORMAL_RANGES['Albumin']['max'])
        platelets = patient_data.get('Platelets', NORMAL_RANGES['Platelets']['max'])
        bmi = patient_data.get('BMI', 25.0)
        alcohol_consumption = patient_data.get('AlcoholConsumption', 0)
        previous_conditions = patient_data.get('PreviousMedicalConditions', 0)
        family_history = patient_data.get('FamilyHistory', 0)
        age = patient_data.get('Age', 40)

        logger.debug(f"Evaluating general rules for patient data: {patient_data}")

        if self.kb.is_lft_elevated('ALT', alt):
            risk_score += 0.15
            evidence.append(f"Elevated ALT ({alt} U/L)")
            if alt > self.kb.normal_ranges['ALT']['max'] * 2:
                risk_score += 0.15
                evidence[-1] += " (Significantly elevated)"

        if self.kb.is_lft_elevated('AST', ast):
            risk_score += 0.15
            evidence.append(f"Elevated AST ({ast} U/L)")
            if ast > self.kb.normal_ranges['AST']['max'] * 2:
                risk_score += 0.15
                evidence[-1] += " (Significantly elevated)"

        if self.kb.is_lft_elevated('ALP', alp):
            risk_score += 0.1
            evidence.append(f"Elevated ALP ({alp} U/L)")

        if self.kb.is_lft_elevated('Bilirubin', bilirubin):
            risk_score += 0.15
            evidence.append(f"Elevated Bilirubin ({bilirubin} mg/dL)")
            if bilirubin > self.kb.normal_ranges['Bilirubin']['max'] * 2:
                risk_score += 0.15
                evidence[-1] += " (Jaundice concern)"

        if self.kb.is_lft_low('Albumin', albumin):
            risk_score += 0.2
            evidence.append(f"Low Albumin ({albumin} g/dL)")

        if self.kb.is_lft_low('Platelets', platelets):
            risk_score += 0.15
            evidence.append(f"Low Platelet Count ({platelets} x10^9/L)")

        if bmi >= 30:
            risk_score += 0.05
            evidence.append("High BMI (Obesity)")

        if alcohol_consumption > 20:
            risk_score += 0.1
            evidence.append(f"Significant Alcohol Consumption ({alcohol_consumption} g/day)")
            if alcohol_consumption > 60:
                risk_score += 0.1
                evidence[-1] += " (Heavy)"

        if previous_conditions == 1:
            risk_score += 0.1
            evidence.append("History of relevant Medical Conditions")

        if family_history == 1:
            risk_score += 0.05
            evidence.append("Family History of Liver Disease")

        risk_score = min(risk_score, 1.0)
        logger.debug(f"General rule-based risk score: {risk_score:.2f}, Evidence: {evidence}")
        return risk_score, evidence

    def evaluate_critical_rules(self, patient_data: Dict[str, Any]) -> tuple[bool, float, list[str]]:
        is_critical = False
        critical_risk_score = 0.0
        critical_evidence = []

        alt = patient_data.get('ALT', NORMAL_RANGES['ALT']['min'])
        ast = patient_data.get('AST', NORMAL_RANGES['AST']['min'])
        albumin = patient_data.get('Albumin', NORMAL_RANGES['Albumin']['max'])
        bilirubin = patient_data.get('Bilirubin', NORMAL_RANGES['Bilirubin']['min'])
        platelets = patient_data.get('Platelets', NORMAL_RANGES['Platelets']['max'])
        hcv_rna = patient_data.get('HCV_RNA_Viral_Load', 0)

        logger.debug(f"Evaluating critical rules for patient data: {patient_data}")

        if self.kb.is_lft_elevated('ALT', alt) and alt > self.kb.normal_ranges['ALT']['max'] * 10:
            is_critical = True
            critical_risk_score = max(critical_risk_score, 0.95)
            critical_evidence.append(f"Extremely High ALT ({alt} U/L) - Suggests severe acute liver injury.")
            logger.debug("Critical Rule 1 (ALT) triggered.")

        if self.kb.is_lft_elevated('AST', ast) and ast > self.kb.normal_ranges['AST']['max'] * 10:
            is_critical = True
            critical_risk_score = max(critical_risk_score, 0.95)
            critical_evidence.append(f"Extremely High AST ({ast} U/L) - Suggests severe acute liver injury.")
            logger.debug("Critical Rule 1 (AST) triggered.")

        if (albumin < 3.0 and bilirubin > 2.5 and platelets < 100):
            is_critical = True
            critical_risk_score = max(critical_risk_score, 0.98)
            critical_evidence.append(f"Combination of Low Albumin ({albumin} g/dL), High Bilirubin ({bilirubin} mg/dL), and Low Platelets ({platelets} x10^9/L) - Strong indicators of liver decompensation/cirrhosis complications.")
            logger.debug("Critical Rule 2 (Decompensation) triggered.")

        if alt > 0:
            ast_alt_ratio = ast / alt
            if ast_alt_ratio >= 2.0 and (bilirubin > 2.0 or albumin < 3.0):
                is_critical = True
                critical_risk_score = max(critical_risk_score, 0.90)
                critical_evidence.append(f"AST/ALT Ratio of {ast_alt_ratio:.2f} (>=2.0) with other abnormalities (e.g., high bilirubin/low albumin) - Suggests severe liver disease, possibly alcoholic liver disease or advanced cirrhosis.")
                logger.debug("Critical Rule 3 (AST/ALT Ratio) triggered.")

        if albumin < 2.8:
            is_critical = True
            critical_risk_score = max(critical_risk_score, 0.99)
            critical_evidence.append(f"Very Low Albumin ({albumin} g/dL) - Indicative of severe liver synthetic dysfunction.")
            logger.debug("Critical Rule 4 (Very Low Albumin) triggered.")

        if hcv_rna > 100000 and (
            self.kb.is_lft_elevated('ALT', alt) or
            self.kb.is_lft_elevated('AST', ast) or
            self.kb.is_lft_elevated('Bilirubin', bilirubin)
        ):
            is_critical = True
            critical_risk_score = max(critical_risk_score, 0.85)
            critical_evidence.append(f"Very High HCV Viral Load ({hcv_rna} IU/mL) with elevated LFTs - Indicates active infection causing liver damage.")
            logger.debug("Critical Rule 5 (High HCV Viral Load + Damage) triggered.")

        logger.debug(f"Critical evaluation result: is_critical={is_critical}, score={critical_risk_score:.2f}, evidence={critical_evidence}")
        return is_critical, critical_risk_score, critical_evidence

# --- Hybrid Diagnostic System ---
class EnhancedHepatitisCDiagnosticSystem:
    # Changed ML_MODEL and SCALER to class properties for clarity
    def __init__(self, ml_model, scaler):
        self.ml_model = ml_model
        self.scaler = scaler
        self.kb = HepatitisCKnowledgeBase(NORMAL_RANGES)
        self.rule_system = HepatitisCRuleBasedSystem(self.kb)
        logger.info("EnhancedHepatitisCDiagnosticSystem initialized.")

    def _prepare_ml_features(self, patient_data: Dict[str, Any]) -> np.ndarray:
        features_dict = {}
        for feature in ML_FEATURES:
            if feature == 'Gender':
                features_dict[feature] = 1 if patient_data.get('Sex', '').lower() == 'male' else 0
            elif feature == 'HCV_RNA_Viral_Load':
                if patient_data.get('HCV_RNA_Detected') and patient_data.get(feature) is None:
                    features_dict[feature] = 10000
                else:
                    features_dict[feature] = patient_data.get(feature, 0)
            else:
                features_dict[feature] = patient_data.get(feature, 0)
        
        features_df = pd.DataFrame([features_dict])
        features_df = features_df[ML_FEATURES]
        
        scaled_data = self.scaler.transform(features_df)
        logger.debug(f"ML features prepared and scaled. Shape: {scaled_data.shape}")
        return scaled_data

    def _determine_risk_level(self, score: float) -> RiskLevel:
        if score >= 0.9:
            return RiskLevel.CRITICAL
        elif score >= 0.7:
            return RiskLevel.HIGH
        elif score >= 0.4:
            return RiskLevel.MODERATE
        elif score >= 0.1:
            return RiskLevel.LOW
        else:
            return RiskLevel.VERY_LOW

    def _get_recommendation(self, overall_risk_level: RiskLevel, critical_evidence: List[str], hcv_detected: bool) -> str:
        recommendations = []
        
        if overall_risk_level == RiskLevel.CRITICAL:
            recommendations.append("URGENT: Immediate specialist consultation (Hepatologist/Gastroenterologist) and further diagnostic tests (e.g., liver biopsy, FibroScan, advanced imaging) are highly recommended. Hospitalization may be necessary for stabilization and management of liver decompensation.")
        elif overall_risk_level == RiskLevel.HIGH:
            recommendations.append("Prompt referral to a Hepatologist/Gastroenterologist for comprehensive evaluation and management is strongly advised. Consider additional tests like viral load quantification, liver imaging, and fibrosis assessment.")
        elif overall_risk_level == RiskLevel.MODERATE:
            recommendations.append("Referral to a primary care physician with expertise in liver health or a general gastroenterologist for further workup. Lifestyle modifications (e.g., alcohol cessation, diet, exercise) are recommended. Monitor LFTs closely.")
        elif overall_risk_level == RiskLevel.LOW:
            recommendations.append("Continue monitoring liver function periodically (e.g., annual check-up). Advise on healthy lifestyle habits (balanced diet, regular exercise, moderate alcohol intake).")
        elif overall_risk_level == RiskLevel.VERY_LOW:
            recommendations.append("General health advice. No immediate liver-specific concerns based on current data. Continue routine health check-ups.")

        if critical_evidence:
            recommendations.append(f"Specific critical findings detected: {'; '.join(critical_evidence)}.")

        if hcv_detected:
            recommendations.append("Given the detection of Hepatitis C, direct-acting antiviral (DAA) therapy consultation with an infectious disease specialist or hepatologist is recommended for potential cure.")
        elif hcv_detected is False and overall_risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.append("Despite no Hepatitis C detected (by ML model on available data), the significant liver health risk requires thorough investigation for other causes of liver damage (e.g., NAFLD/NASH, alcoholic liver disease, autoimmune hepatitis, drug-induced liver injury, other viral hepatitides).")

        return " ".join(recommendations)

    def diagnose(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        results = {}
        logger.info(f"Starting diagnosis for patient: {patient_data.get('Age', 'N/A')} y.o. {patient_data.get('Sex', 'N/A')}")

        # 1. Hepatitis C Detection (ML Model)
        processed_data_ml = self._prepare_ml_features(patient_data)
        
        # Use the appropriate model based on availability (TensorFlow or RandomForest)
        if self.ml_model == hepatitis_c_tf_model:
            ml_prediction_proba = self.ml_model.predict(processed_data_ml)[0][0]
            ml_prediction_class = 1 if ml_prediction_proba >= 0.5 else 0
        else: # Assumes RandomForest or another scikit-learn model
            ml_prediction_proba = self.ml_model.predict_proba(processed_data_ml)[0][1]
            ml_prediction_class = self.ml_model.predict(processed_data_ml)[0]

        hcv_detected = bool(ml_prediction_class)
        results['hepatitis_c_detected_ml'] = hcv_detected
        results['ml_probability_hcv'] = float(f"{ml_prediction_proba:.4f}")
        results['hepatitis_c_diagnosis_label'] = "Hepatitis C Detected" if hcv_detected else "No Hepatitis C Detected"
        logger.debug(f"ML Hepatitis C Prediction: Label='{results['hepatitis_c_diagnosis_label']}', Probability={ml_prediction_proba:.4f}")

        # 2. General Liver Health Risk (Rule-Based System)
        rule_risk_score, rule_evidence = self.rule_system.evaluate_rules(patient_data)
        is_critical, critical_risk_from_rules, critical_evidence = self.rule_system.evaluate_critical_rules(patient_data)

        results['rule_based_general_liver_risk_score'] = float(f"{rule_risk_score:.4f}")
        results['rule_based_evidence'] = rule_evidence
        results['is_critical_from_rules'] = is_critical
        results['critical_risk_from_rules'] = float(f"{critical_risk_from_rules:.4f}")
        results['critical_evidence'] = critical_evidence
        logger.debug(f"Rule-based general risk: {rule_risk_score:.4f}, Critical: {is_critical} (Score: {critical_risk_from_rules:.4f})")

        # 3. Hybrid Aggregation for Overall Liver Health Risk
        if is_critical:
            final_overall_risk_score = max(critical_risk_from_rules, ml_prediction_proba, rule_risk_score)
            results['overall_decision_method'] = "Rule-based (Critical Override)"
            results['overall_evidence'] = list(set(critical_evidence + rule_evidence))
        else:
            ml_weight = 0.6
            rule_weight = 0.4
            final_overall_risk_score = (ml_prediction_proba * ml_weight) + (rule_risk_score * rule_weight)
            results['overall_decision_method'] = "Hybrid (ML + Rule-based)"
            results['overall_evidence'] = rule_evidence

        results['final_overall_risk_score'] = float(f"{final_overall_risk_score:.4f}")
        
        risk_level_enum = self._determine_risk_level(final_overall_risk_score)
        results['overall_health_risk_level'] = risk_level_enum.value
        results['overall_health_risk_level_label'] = risk_level_enum.value

        logger.info(f"Final Overall Liver Health Risk: '{results['overall_health_risk_level_label']}' (Score: {results['final_overall_risk_score']:.4f})")

        # 4. Generate Recommendation
        results['recommendation'] = self._get_recommendation(
            risk_level_enum,
            critical_evidence,
            hcv_detected
        )

        logger.info("Diagnosis complete.")
        return results

# --- Global instance of the diagnostic system ---
# We instantiate this after loading the artifacts
knowledge_base_global = HepatitisCKnowledgeBase(NORMAL_RANGES)
rule_based_system_global = HepatitisCRuleBasedSystem(knowledge_base_global)

# Use the loaded global artifacts to initialize the diagnostic system
# We prioritize the TensorFlow model if available, otherwise use the RandomForest model
if hepatitis_c_tf_model:
    ml_model_to_use = hepatitis_c_tf_model
else:
    ml_model_to_use = hepatitis_c_rf_model

hepatitis_c_diagnostic_system = EnhancedHepatitisCDiagnosticSystem(
    ml_model=ml_model_to_use, 
    scaler=hepatitis_c_scaler
)

# --- Expose the prediction function for app.py to import ---
def predict_hepatitis_c(patient_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predicts Hepatitis C status and overall liver health risk using the hybrid diagnostic system.
    This function is intended to be called by the Flask API.
    """
    try:
        if hepatitis_c_diagnostic_system.ml_model is None or hepatitis_c_diagnostic_system.scaler is None:
            raise RuntimeError("Hepatitis C model artifacts are not available.")

        diagnosis_results = hepatitis_c_diagnostic_system.diagnose(patient_data)
        return diagnosis_results
    except Exception as e:
        logger.error(f"Error during Hepatitis C prediction: {e}", exc_info=True)
        # Return an error structure that app.py can handle
        return {"error": "Prediction failed", "details": str(e), "status_code": 500}

# --- Main Execution Block (for direct testing of this script) ---
if __name__ == "__main__":
    print("\n--- Running Diagnostic Test Cases for Hepatitis C Prediction ---")

    # --- Test Patient Data (as discussed) ---
    patient_data_1 = { # Low risk, no HCV
        'Age': 35, 'Sex': 'female', 'BMI': 22.5, 'Smoking': 0, 'AlcoholConsumption': 5,
        'PreviousMedicalConditions': 0, 'FamilyHistory': 0, 'ALT': 25, 'AST': 20, 'ALP': 80,
        'Bilirubin': 0.8, 'Albumin': 4.5, 'Platelets': 250, 'HCV_RNA_Viral_Load': 0
    }
    
    patient_data_2 = { # Moderate risk, potential for HCV
        'Age': 50, 'Sex': 'male', 'BMI': 31.0, 'Smoking': 1, 'AlcoholConsumption': 30,
        'PreviousMedicalConditions': 1, 'FamilyHistory': 0, 'ALT': 65, 'AST': 55, 'ALP': 150,
        'Bilirubin': 1.5, 'Albumin': 3.8, 'Platelets': 140, 'HCV_RNA_Viral_Load': 100000
    }
    
    # Critical risk case
    patient_data_3 = {
        'Age': 60, 'Sex': 'male', 'BMI': 25.0, 'Smoking': 1, 'AlcoholConsumption': 80,
        'PreviousMedicalConditions': 1, 'FamilyHistory': 1, 'ALT': 500, 'AST': 1200, 'ALP': 300,
        'Bilirubin': 5.5, 'Albumin': 2.5, 'Platelets': 80, 'HCV_RNA_Viral_Load': 500000
    }
    
    # Run tests and print results
    print("\n--- Test Case 1: Low Risk Patient ---")
    result_1 = predict_hepatitis_c(patient_data_1)
    print(f"Prediction Result: {result_1}")

    print("\n--- Test Case 2: Moderate Risk Patient with potential HCV ---")
    result_2 = predict_hepatitis_c(patient_data_2)
    print(f"Prediction Result: {result_2}")

    print("\n--- Test Case 3: Critical Risk Patient ---")
    result_3 = predict_hepatitis_c(patient_data_3)
    print(f"Prediction Result: {result_3}")