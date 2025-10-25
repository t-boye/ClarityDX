import pandas as pd
import numpy as np
import logging
from enum import Enum
from typing import Dict, Any, Union, List, Optional
import requests
import joblib
from io import BytesIO

# Try to import TensorFlow, provide helpful error if not installed
try:
    from tensorflow import keras
    _tensorflow_available = True
except ImportError:
    _tensorflow_available = False
    print("Warning: TensorFlow not found. The TensorFlow model prediction will be skipped.")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

# --- Knowledge Base for Rule-Based System ---
class HepatitisCKnowledgeBase:
    """
    A knowledge base containing normal reference ranges and helper methods.
    """
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
    """
    A rule-based expert system to evaluate a patient's general liver health risk.
    """
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        logger.info("HepatitisCRuleBasedSystem initialized.")

    def evaluate_rules(self, patient_data: Dict[str, Any]) -> tuple[float, list[str]]:
        risk_score = 0.0
        evidence = []
        
        # Safely get values with default fallbacks
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

        # Safely get values with default fallbacks
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
    """
    Combines an ML model prediction with a rule-based expert system for a comprehensive diagnosis.
    """
    def __init__(self, ml_model: Any, scaler: Any, ml_features: List[str]):
        if ml_model is None or scaler is None or not ml_features:
            raise ValueError("ML model, scaler, and feature names must be provided.")
        self.ml_model = ml_model
        self.scaler = scaler
        self.ml_features = ml_features
        self.kb = HepatitisCKnowledgeBase(NORMAL_RANGES)
        self.rule_system = HepatitisCRuleBasedSystem(self.kb)
        logger.info("EnhancedHepatitisCDiagnosticSystem initialized with provided artifacts.")

    def _prepare_ml_features(self, patient_data: Dict[str, Any]) -> np.ndarray:
        features_dict = {}
        for feature in self.ml_features:
            if feature == 'Gender':
                features_dict[feature] = 1 if patient_data.get('Sex', '').lower() == 'male' else 0
            elif feature == 'HCV_RNA_Viral_Load':
                if patient_data.get('HCV_RNA_Detected') and patient_data.get(feature) is None:
                    features_dict[feature] = 10000 # Default viral load for detected but unspecified
                else:
                    features_dict[feature] = patient_data.get(feature, 0)
            else:
                features_dict[feature] = patient_data.get(feature, 0)
        
        features_df = pd.DataFrame([features_dict])
        features_df = features_df[self.ml_features]
        
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
        
        # Use the appropriate model based on its type (TensorFlow or Scikit-learn)
        if _tensorflow_available and isinstance(self.ml_model, keras.Model):
            ml_prediction_proba = self.ml_model.predict(processed_data_ml)[0][0]
            ml_prediction_class = 1 if ml_prediction_proba >= 0.5 else 0
        else: # Assumes scikit-learn model
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

# --- Main entry-point function for the new approach ---
def predict_hepatitis_c(patient_data: Dict[str, Any], models: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predicts Hepatitis C status and overall liver health risk using the hybrid diagnostic system.
    This function is intended to be called by the main application, which provides the model artifacts.

    Args:
        patient_data (Dict[str, Any]): A dictionary containing patient data for diagnosis.
        models (Dict[str, Any]): A dictionary containing all pre-loaded model artifacts.
                                 Expected keys: 'rf_model' or 'tf_model', 'scaler', 'feature_names'.
    
    Returns:
        Dict[str, Any]: A dictionary containing the diagnosis results, including ML prediction,
                        rule-based risk, and a combined overall risk and recommendation.
    """
    try:
        # Prioritize the TensorFlow model if available, otherwise use the RandomForest model
        ml_model = models.get('tf_model') or models.get('rf_model')
        scaler = models.get('scaler')
        feature_names = models.get('feature_names')

        if ml_model is None or scaler is None or feature_names is None:
            raise RuntimeError("Required model artifacts (rf_model/tf_model, scaler, feature_names) are missing.")
        
        # Instantiate the diagnostic system with the provided artifacts
        hepatitis_c_diagnostic_system = EnhancedHepatitisCDiagnosticSystem(
            ml_model=ml_model,
            scaler=scaler,
            ml_features=feature_names
        )

        diagnosis_results = hepatitis_c_diagnostic_system.diagnose(patient_data)
        return diagnosis_results
    except Exception as e:
        logger.error(f"Error during Hepatitis C prediction: {e}", exc_info=True)
        # Return an error structure that app.py can handle
        return {"error": "Prediction failed", "details": str(e), "status_code": 500}

# --- Main Execution Block (for direct testing of this script) ---
# NOTE: This block is for demonstration only and simulates the main app.py file.
if __name__ == "__main__":
    print("\n--- Running Diagnostic Test Cases for Hepatitis C Prediction ---")
    
    # We must simulate the models dictionary that app.py would pass.
    # In a real scenario, these would be loaded from files/URLs by app.py.
    class DummyScaler:
        def transform(self, df):
            # A dummy scaler that returns the input as is
            return df.values

    class DummyRFModel:
        def predict(self, data):
            return np.array([1]) # Simulates a positive prediction
        def predict_proba(self, data):
            return np.array([[0.2, 0.8]]) # Simulates a high probability of HCV

    class DummyTFModel(keras.Model):
        def predict(self, data):
            return np.array([[0.8]]) # Simulates a high probability of HCV

    # Simulating the models dictionary
    simulated_models = {
        'rf_model': DummyRFModel(),
        'tf_model': DummyTFModel(),
        'scaler': DummyScaler(),
        'feature_names': ML_FEATURES
    }

    print("Note: The models are dummy objects for local testing.")

    # --- Test Patient Data ---
    patient_data_1 = { # Low risk, no HCV
        'Age': 35, 'Sex': 'female', 'BMI': 22.5, 'Smoking': 0, 'AlcoholConsumption': 5,
        'PreviousMedicalConditions': 0, 'FamilyHistory': 0, 'ALT': 25, 'AST': 20, 'ALP': 80,
        'Bilirubin': 0.8, 'Albumin': 4.5, 'Platelets': 250, 'HCV_RNA_Viral_Load': 0, 'HCV_RNA_Detected': False
    }
    
    patient_data_2 = { # Moderate risk, potential for HCV
        'Age': 50, 'Sex': 'male', 'BMI': 31.0, 'Smoking': 1, 'AlcoholConsumption': 30,
        'PreviousMedicalConditions': 1, 'FamilyHistory': 0, 'ALT': 65, 'AST': 55, 'ALP': 150,
        'Bilirubin': 1.5, 'Albumin': 3.8, 'Platelets': 140, 'HCV_RNA_Viral_Load': 100000, 'HCV_RNA_Detected': True
    }
    
    # Critical risk case
    patient_data_3 = {
        'Age': 60, 'Sex': 'male', 'BMI': 25.0, 'Smoking': 1, 'AlcoholConsumption': 80,
        'PreviousMedicalConditions': 1, 'FamilyHistory': 1, 'ALT': 500, 'AST': 1200, 'ALP': 300,
        'Bilirubin': 5.5, 'Albumin': 2.5, 'Platelets': 80, 'HCV_RNA_Viral_Load': 500000, 'HCV_RNA_Detected': True
    }
    
    # Run tests and print results
    print("\n--- Test Case 1: Low Risk Patient ---")
    result_1 = predict_hepatitis_c(patient_data_1, simulated_models)
    print(f"Prediction Result: {result_1}")

    print("\n--- Test Case 2: Moderate Risk Patient with potential HCV ---")
    result_2 = predict_hepatitis_c(patient_data_2, simulated_models)
    print(f"Prediction Result: {result_2}")

    print("\n--- Test Case 3: Critical Risk Patient ---")
    result_3 = predict_hepatitis_c(patient_data_3, simulated_models)
    print(f"Prediction Result: {result_3}")