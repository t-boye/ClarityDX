import pandas as pd
import numpy as np
import os
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
from enum import Enum
import logging
from typing import Dict, Any, Union, List

# Configure logging for better insights
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Global Artifact Paths ---
# Get the directory of the current file (hepatitis_c_prediction.py)
CURRENT_FILE_DIR = os.path.dirname(os.path.abspath(__file__))

# Go up one level to get to the 'backend' directory
BACKEND_ROOT_DIR = os.path.abspath(os.path.join(CURRENT_FILE_DIR, '..'))

# Now, construct the path to the specific Hepatitis C model directory
# within the main 'models' directory of the backend.
# Renamed from HEPATITIS_C_MODEL_DIR to MODEL_DIR for consistency with the rest of the file
# and previous error context, if you prefer HEPATITIS_C_MODEL_DIR, ensure to use it everywhere.
MODEL_DIR = os.path.join(BACKEND_ROOT_DIR, "models", "hepatitis_c_model")

# Define paths for model artifacts using the corrected directory
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
ML_MODEL_PATH = os.path.join(MODEL_DIR, "random_forest_model.pkl")

# Define feature columns for the ML model (must match training data)
ML_FEATURES = [
    'Age', 'Gender', 'BMI', 'Smoking', 'AlcoholConsumption',
    'PreviousMedicalConditions', 'FamilyHistory', 'ALT', 'AST', 'ALP',
    'Bilirubin', 'Albumin', 'Platelets', 'HCV_RNA_Viral_Load'
]

# Normal/Reference Ranges for LFTs (Approximate values for adults, often vary by lab)
# These are used for rule-based interpretations
NORMAL_RANGES = {
    'ALT': {'min': 7, 'max': 55},     # Units/L
    'AST': {'min': 8, 'max': 48},     # Units/L
    'ALP': {'min': 40, 'max': 129},   # Units/L
    'Bilirubin': {'min': 0.1, 'max': 1.2}, # mg/dL
    'Albumin': {'min': 3.5, 'max': 5.0},   # g/dL
    'Platelets': {'min': 150, 'max': 450} # x10^9/L
}

# Define risk level enumeration for clear diagnosis
class RiskLevel(Enum):
    VERY_LOW = "Very Low Risk"
    LOW = "Low Risk"
    MODERATE = "Moderate Risk"
    HIGH = "High Risk"
    CRITICAL = "Critical Risk"

# --- ML Model Management (Simulated for demonstration) ---
def create_dummy_model_artifacts():
    """
    Creates dummy ML model and scaler files for demonstration purposes
    if they don't exist. In a real scenario, these would be trained and saved.
    """
    logger.info("Checking for dummy model artifacts...")
    
    # Ensure the model directory exists
    os.makedirs(MODEL_DIR, exist_ok=True) # MODEL_DIR is now correctly used here

    # Generate dummy data for training
    np.random.seed(42)
    num_samples = 200 # Increased sample size for slightly better dummy model
    data = {
        'Age': np.random.randint(20, 70, num_samples),
        'Gender': np.random.choice([0, 1], num_samples), # 0 for Female, 1 for Male
        'BMI': np.random.uniform(18.0, 35.0, num_samples),
        'Smoking': np.random.choice([0, 1], num_samples),
        'AlcoholConsumption': np.random.uniform(0, 50, num_samples), # g/day
        'PreviousMedicalConditions': np.random.choice([0, 1], num_samples),
        'FamilyHistory': np.random.choice([0, 1], num_samples),
        'ALT': np.random.uniform(10, 200, num_samples),
        'AST': np.random.uniform(10, 180, num_samples),
        'ALP': np.random.uniform(50, 250, num_samples),
        'Bilirubin': np.random.uniform(0.5, 3.0, num_samples),
        'Albumin': np.random.uniform(2.5, 5.0, num_samples),
        'Platelets': np.random.uniform(100, 400, num_samples),
        'HCV_RNA_Viral_Load': np.random.uniform(0, 1000000, num_samples) # IU/mL - wider range for viral load
    }
    df = pd.DataFrame(data)

    # Create a dummy target variable for Hepatitis C (simulated logic)
    # Higher viral load, higher LFTs, and certain risk factors increase probability
    df['HCV_Positive'] = ((df['HCV_RNA_Viral_Load'] > 50000) * 0.7 + # Stronger influence for higher viral load
                          (df['ALT'] > NORMAL_RANGES['ALT']['max'] * 1.5) * 0.15 +
                          (df['AST'] > NORMAL_RANGES['AST']['max'] * 1.5) * 0.1 +
                          (df['AlcoholConsumption'] > 25) * 0.05 +
                          (df['Smoking'] == 1) * 0.02 +
                          (df['Age'] > 50) * 0.03).apply(lambda x: 1 if x > 0.5 else 0)

    X = df[ML_FEATURES]
    y = df['HCV_Positive']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Check if scaler exists, if not, create and save
    if not os.path.exists(SCALER_PATH):
        scaler = StandardScaler()
        scaler.fit(X_train)
        joblib.dump(scaler, SCALER_PATH)
        logger.info(f"Dummy StandardScaler saved to {SCALER_PATH}")
    else:
        logger.info(f"Scaler already exists at {SCALER_PATH}. Skipping dummy creation.")

    # Check if model exists, if not, create and save
    if not os.path.exists(ML_MODEL_PATH):
        model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced') # Use class_weight for dummy model
        # Use the already fit scaler for dummy model training data
        model.fit(scaler.transform(X_train), y_train) 
        joblib.dump(model, ML_MODEL_PATH)
        logger.info(f"Dummy RandomForestClassifier saved to {ML_MODEL_PATH}")
    else:
        logger.info(f"Model already exists at {ML_MODEL_PATH}. Skipping dummy creation.")

    logger.info("Dummy ML model and scaler creation check completed.")


def load_ml_model_and_scaler():
    """Loads the pre-trained ML model and scaler, or creates dummies if not found."""
    # First, ensure the model directory exists
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    # Check if artifacts exist. If not, trigger dummy creation.
    if not (os.path.exists(ML_MODEL_PATH) and os.path.exists(SCALER_PATH)):
        logger.warning("ML model or scaler not found. Attempting to create dummy artifacts.")
        create_dummy_model_artifacts()

    try:
        model = joblib.load(ML_MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        logger.info("ML model and scaler loaded successfully.")
        return model, scaler
    except Exception as e:
        logger.error(f"Failed to load ML model or scaler: {e}", exc_info=True)
        raise # Re-raise the exception after logging

# Load ML model and scaler once at the start of the application
ML_MODEL, SCALER = load_ml_model_and_scaler()

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
        """
        Evaluates general liver health rules.
        Returns a base risk score (0-1) and a list of contributing factors/evidence.
        """
        risk_score = 0.0
        evidence = []
        
        # Ensure all relevant keys are present for robust evaluation
        # Provide sensible defaults for missing data to avoid errors
        alt = patient_data.get('ALT', NORMAL_RANGES['ALT']['min'])
        ast = patient_data.get('AST', NORMAL_RANGES['AST']['min'])
        alp = patient_data.get('ALP', NORMAL_RANGES['ALP']['min'])
        bilirubin = patient_data.get('Bilirubin', NORMAL_RANGES['Bilirubin']['min'])
        albumin = patient_data.get('Albumin', NORMAL_RANGES['Albumin']['max'])
        platelets = patient_data.get('Platelets', NORMAL_RANGES['Platelets']['max'])
        bmi = patient_data.get('BMI', 25.0)
        alcohol_consumption = patient_data.get('AlcoholConsumption', 0) # g/day
        previous_conditions = patient_data.get('PreviousMedicalConditions', 0)
        family_history = patient_data.get('FamilyHistory', 0)
        age = patient_data.get('Age', 40)

        logger.debug(f"Evaluating general rules for patient data: {patient_data}")

        # --- Basic LFT Abnormalities ---
        if self.kb.is_lft_elevated('ALT', alt):
            risk_score += 0.15
            evidence.append(f"Elevated ALT ({alt} U/L)")
            if alt > self.kb.normal_ranges['ALT']['max'] * 2: # Significantly elevated
                risk_score += 0.15
                evidence[-1] += " (Significantly elevated)"

        if self.kb.is_lft_elevated('AST', ast):
            risk_score += 0.15
            evidence.append(f"Elevated AST ({ast} U/L)")
            if ast > self.kb.normal_ranges['AST']['max'] * 2: # Significantly elevated
                risk_score += 0.15
                evidence[-1] += " (Significantly elevated)"

        if self.kb.is_lft_elevated('ALP', alp):
            risk_score += 0.1
            evidence.append(f"Elevated ALP ({alp} U/L)")

        if self.kb.is_lft_elevated('Bilirubin', bilirubin):
            risk_score += 0.15
            evidence.append(f"Elevated Bilirubin ({bilirubin} mg/dL)")
            if bilirubin > self.kb.normal_ranges['Bilirubin']['max'] * 2: # Jaundice concern
                risk_score += 0.15
                evidence[-1] += " (Jaundice concern)"

        if self.kb.is_lft_low('Albumin', albumin):
            risk_score += 0.2
            evidence.append(f"Low Albumin ({albumin} g/dL)")

        if self.kb.is_lft_low('Platelets', platelets):
            risk_score += 0.15
            evidence.append(f"Low Platelet Count ({platelets} x10^9/L)")

        # --- Risk Factors ---
        if bmi >= 30:
            risk_score += 0.05
            evidence.append("High BMI (Obesity)")

        if alcohol_consumption > 20: # g/day, indicative of significant intake
            risk_score += 0.1
            evidence.append(f"Significant Alcohol Consumption ({alcohol_consumption} g/day)")
            if alcohol_consumption > 60: # Heavy consumption
                risk_score += 0.1
                evidence[-1] += " (Heavy)"

        if previous_conditions == 1: # Assuming 1 means presence of relevant conditions
            risk_score += 0.1
            evidence.append("History of relevant Medical Conditions")

        if family_history == 1: # Assuming 1 means presence of family history
            risk_score += 0.05
            evidence.append("Family History of Liver Disease")

        # Cap risk score at 1.0
        risk_score = min(risk_score, 1.0)
        logger.debug(f"General rule-based risk score: {risk_score:.2f}, Evidence: {evidence}")
        return risk_score, evidence

    def evaluate_critical_rules(self, patient_data: Dict[str, Any]) -> tuple[bool, float, list[str]]:
        """
        Evaluates critical liver health rules that might indicate severe,
        immediate concern, overriding general risk.
        Returns (is_critical: bool, critical_risk_score: float, critical_evidence: list)
        """
        is_critical = False
        critical_risk_score = 0.0
        critical_evidence = []

        # Use .get with default values to safely handle potentially missing data
        alt = patient_data.get('ALT', NORMAL_RANGES['ALT']['min'])
        ast = patient_data.get('AST', NORMAL_RANGES['AST']['min'])
        albumin = patient_data.get('Albumin', NORMAL_RANGES['Albumin']['max'])
        bilirubin = patient_data.get('Bilirubin', NORMAL_RANGES['Bilirubin']['min'])
        platelets = patient_data.get('Platelets', NORMAL_RANGES['Platelets']['max'])
        hcv_rna = patient_data.get('HCV_RNA_Viral_Load', 0)

        logger.debug(f"Evaluating critical rules for patient data: {patient_data}")

        # Rule 1: Extreme LFT elevations (Acute Liver Failure/Severe Hepatitis)
        # Using a higher threshold for "critical" elevation (e.g., 10x normal)
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

        # Rule 2: Signs of Liver Decompensation (Cirrhosis complications)
        # Low Albumin + High Bilirubin + Low Platelets are strong indicators
        if (albumin < 3.0 and bilirubin > 2.5 and platelets < 100):
            is_critical = True
            critical_risk_score = max(critical_risk_score, 0.98)
            critical_evidence.append(f"Combination of Low Albumin ({albumin} g/dL), High Bilirubin ({bilirubin} mg/dL), and Low Platelets ({platelets} x10^9/L) - Strong indicators of liver decompensation/cirrhosis complications.")
            logger.debug("Critical Rule 2 (Decompensation) triggered.")

        # Rule 3: AST/ALT Ratio > 2 with other signs (e.g., severe alcoholic hepatitis, advanced cirrhosis)
        # This is often associated with alcoholic liver disease but can occur in advanced cirrhosis of any etiology
        if alt > 0: # Avoid division by zero
            ast_alt_ratio = ast / alt
            if ast_alt_ratio >= 2.0 and (bilirubin > 2.0 or albumin < 3.0):
                is_critical = True
                critical_risk_score = max(critical_risk_score, 0.90)
                critical_evidence.append(f"AST/ALT Ratio of {ast_alt_ratio:.2f} (>=2.0) with other abnormalities (e.g., high bilirubin/low albumin) - Suggests severe liver disease, possibly alcoholic liver disease or advanced cirrhosis.")
                logger.debug("Critical Rule 3 (AST/ALT Ratio) triggered.")

        # Rule 4: Very low Albumin (severe synthetic dysfunction)
        if albumin < 2.8: # Child-Pugh Class C range
            is_critical = True
            critical_risk_score = max(critical_risk_score, 0.99)
            critical_evidence.append(f"Very Low Albumin ({albumin} g/dL) - Indicative of severe liver synthetic dysfunction.")
            logger.debug("Critical Rule 4 (Very Low Albumin) triggered.")

        # Rule 5: High Viral Load with any signs of damage
        if hcv_rna > 100000 and (
            self.kb.is_lft_elevated('ALT', alt) or
            self.kb.is_lft_elevated('AST', ast) or
            self.kb.is_lft_elevated('Bilirubin', bilirubin)
        ):
            # This rule flags active infection *with* liver damage, potentially critical if damage is significant
            is_critical = True
            critical_risk_score = max(critical_risk_score, 0.85) # A high but not always highest critical score
            critical_evidence.append(f"Very High HCV Viral Load ({hcv_rna} IU/mL) with elevated LFTs - Indicates active infection causing liver damage.")
            logger.debug("Critical Rule 5 (High HCV Viral Load + Damage) triggered.")

        logger.debug(f"Critical evaluation result: is_critical={is_critical}, score={critical_risk_score:.2f}, evidence={critical_evidence}")
        return is_critical, critical_risk_score, critical_evidence

# --- Hybrid Diagnostic System ---
class EnhancedHepatitisCDiagnosticSystem:
    def __init__(self, ml_model, scaler, knowledge_base, rule_based_system):
        self.ml_model = ml_model
        self.scaler = scaler
        self.kb = knowledge_base
        self.rule_system = rule_based_system
        logger.info("EnhancedHepatitisCDiagnosticSystem initialized.")

    def _prepare_ml_features(self, patient_data: Dict[str, Any]) -> np.ndarray: # Changed return type to np.ndarray
        """Prepares patient data for the ML model, handling missing features."""
        features_dict = {}
        for feature in ML_FEATURES:
            # Use .get() with a default value (e.g., 0 or mean/median of training data)
            # Gender: 0 for female, 1 for male. Convert string 'Sex' to int 'Gender'.
            if feature == 'Gender':
                features_dict[feature] = 1 if patient_data.get('Sex', '').lower() == 'male' else 0
            elif feature == 'HCV_RNA_Viral_Load':
                # Map boolean 'HCV_RNA_Detected' to a dummy viral load if viral load itself is missing
                if patient_data.get('HCV_RNA_Detected') and patient_data.get(feature) is None:
                    features_dict[feature] = 10000 # Assume a detectable but not necessarily high load
                else:
                    features_dict[feature] = patient_data.get(feature, 0) # Default to 0 if not provided
            else:
                features_dict[feature] = patient_data.get(feature, 0) # Default for other numerical features
        
        # Create a DataFrame from the prepared dictionary
        features_df = pd.DataFrame([features_dict])
        
        # Ensure column order matches ML_FEATURES for scaler and model
        features_df = features_df[ML_FEATURES]
        
        scaled_data = self.scaler.transform(features_df)
        logger.debug(f"ML features prepared and scaled. Shape: {scaled_data.shape}")
        return scaled_data

    def _determine_risk_level(self, score: float) -> RiskLevel:
        """Maps a numerical risk score (0-1) to a RiskLevel enum."""
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
        """Provides actionable recommendations based on risk level and specific findings."""
        recommendations = []
        
        # General risk level recommendations
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

        # Specific additions based on critical findings or HCV detection
        if critical_evidence:
            recommendations.append(f"Specific critical findings detected: {'; '.join(critical_evidence)}.")

        if hcv_detected:
            recommendations.append("Given the detection of Hepatitis C, direct-acting antiviral (DAA) therapy consultation with an infectious disease specialist or hepatologist is recommended for potential cure.")
        elif hcv_detected is False and overall_risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.append("Despite no Hepatitis C detected (by ML model on available data), the significant liver health risk requires thorough investigation for other causes of liver damage (e.g., NAFLD/NASH, alcoholic liver disease, autoimmune hepatitis, drug-induced liver injury, other viral hepatitides).")

        return " ".join(recommendations)

    def diagnose(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provides a dual diagnosis for Hepatitis C detection and general liver health risk.
        """
        results = {}
        logger.info(f"Starting diagnosis for patient: {patient_data.get('Age', 'N/A')} y.o. {patient_data.get('Sex', 'N/A')}")

        # 1. Hepatitis C Detection (ML Model)
        processed_data_ml = self._prepare_ml_features(patient_data)
        ml_prediction_proba = self.ml_model.predict_proba(processed_data_ml)[0][1] # Probability of HCV_Positive (class 1)
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
        # If critical rules fire, they take precedence for the overall risk score
        if is_critical:
            final_overall_risk_score = max(critical_risk_from_rules, ml_prediction_proba, rule_risk_score)
            results['overall_decision_method'] = "Rule-based (Critical Override)"
            # Combine critical evidence first, then add general evidence that is not already covered
            results['overall_evidence'] = list(set(critical_evidence + rule_evidence)) 
        else:
            # If no critical rules, combine ML and rule-based scores
            # Assign weights (can be tuned)
            ml_weight = 0.6
            rule_weight = 0.4
            final_overall_risk_score = (ml_prediction_proba * ml_weight) + (rule_risk_score * rule_weight)
            results['overall_decision_method'] = "Hybrid (ML + Rule-based)"
            results['overall_evidence'] = rule_evidence

        results['final_overall_risk_score'] = float(f"{final_overall_risk_score:.4f}")
        
        # --- FIX APPLIED HERE: Convert RiskLevel enum to its string value ---
        risk_level_enum = self._determine_risk_level(final_overall_risk_score)
        results['overall_health_risk_level'] = risk_level_enum.value # Store the string value
        # Retain overall_health_risk_level_label for clarity if needed, though it's now redundant
        results['overall_health_risk_level_label'] = risk_level_enum.value
        # --- END FIX ---

        logger.info(f"Final Overall Liver Health Risk: '{results['overall_health_risk_level_label']}' (Score: {results['final_overall_risk_score']:.4f})")

        # 4. Generate Recommendation
        results['recommendation'] = self._get_recommendation(
            risk_level_enum, # Pass the actual enum for recommendation logic
            critical_evidence,
            hcv_detected
        )

        logger.info("Diagnosis complete.")
        return results

# --- Global instance of the diagnostic system ---
# This ensures the model and scaler are loaded only once.
knowledge_base_global = HepatitisCKnowledgeBase(NORMAL_RANGES)
rule_based_system_global = HepatitisCRuleBasedSystem(knowledge_base_global)
hepatitis_c_diagnostic_system = EnhancedHepatitisCDiagnosticSystem(ML_MODEL, SCALER, knowledge_base_global, rule_based_system_global)

# --- Expose the prediction function for app.py to import ---
def predict_hepatitis_c(patient_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predicts Hepatitis C status and overall liver health risk using the hybrid diagnostic system.
    This function is intended to be called by the Flask API.
    """
    try:
        diagnosis_results = hepatitis_c_diagnostic_system.diagnose(patient_data)
        return diagnosis_results
    except Exception as e:
        logger.error(f"Error during Hepatitis C prediction: {e}")
        # Return an error structure that app.py can handle
        return {"error": "Prediction failed", "details": str(e)}

# --- Main Execution Block (for direct testing of this script) ---
if __name__ == "__main__":
    print("\n--- Running Diagnostic Test Cases for Hepatitis C Prediction ---")

    # --- Test Patient Data (as discussed) ---
    patient_data_1 = { # Low risk, no HCV
        'Age': 35, 'Sex': 'female', 'BMI': 22.5, 'Smoking': 0, 'AlcoholConsumption': 5,
        'PreviousMedicalConditions': 0, 'FamilyHistory': 0, 'ALT': 25, 'AST': 20, 'ALP': 80,
        'Bilirubin': 0.8, 'Albumin': 4.5, 'Platelets': 250, 'HCV_RNA_Viral_Load': 0
    }

    patient_data_2 = { # Moderate risk, potential HCV
        'Age': 45, 'Sex': 'male', 'BMI': 28.0, 'Smoking': 1, 'AlcoholConsumption': 30,
        'PreviousMedicalConditions': 1, 'FamilyHistory': 1, 'ALT': 70, 'AST': 60, 'ALP': 150,
        'Bilirubin': 1.5, 'Albumin': 3.8, 'Platelets': 180, 'HCV_RNA_Viral_Load': 15000
    }

    patient_data_3 = { # High risk, confirmed HCV
        'Age': 55, 'Sex': 'female', 'BMI': 31.0, 'Smoking': 0, 'AlcoholConsumption': 10,
        'PreviousMedicalConditions': 1, 'FamilyHistory': 1, 'ALT': 120, 'AST': 100, 'ALP': 200,
        'Bilirubin': 2.5, 'Albumin': 3.2, 'Platelets': 120, 'HCV_RNA_Viral_Load': 500000
    }

    patient_data_4 = { # Critical risk (severe LFTs), but low/no HCV viral load - High Alcohol
        'Age': 60, 'Sex': 'male', 'BMI': 25.0, 'Smoking': 0, 'AlcoholConsumption': 70,
        'PreviousMedicalConditions': 1, 'FamilyHistory': 0, 'ALT': 50, 'AST': 180, 'ALP': 300,
        'Bilirubin': 5.0, 'Albumin': 2.7, 'Platelets': 80, 'HCV_RNA_Viral_Load': 500
    }

    patient_data_5 = { # Critical from rules, even with low HCV_RNA (AST/ALT ratio, low ALB, low platelets, high BIL)
        'Age': 68, 'Sex': 'female', 'BMI': 29.0, 'Smoking': 1, 'AlcoholConsumption': 40,
        'PreviousMedicalConditions': 1, 'FamilyHistory': 1, 'ALT': 30, 'AST': 90, # AST/ALT ratio = 3.0
        'ALP': 180, 'Bilirubin': 3.5, 'Albumin': 2.9, 'Platelets': 95,
        'HCV_RNA_Viral_Load': 800
    }
    
    patient_data_6 = { # Critical risk due to extremely high ALT (e.g., acute drug-induced liver injury, not necessarily HCV)
        'Age': 40, 'Sex': 'male', 'BMI': 24.0, 'Smoking': 0, 'AlcoholConsumption': 0,
        'PreviousMedicalConditions': 0, 'FamilyHistory': 0, 'ALT': 800, 'AST': 400, 'ALP': 100,
        'Bilirubin': 1.5, 'Albumin': 4.0, 'Platelets': 280, 'HCV_RNA_Viral_Load': 0
    }

    # Test case for missing values (will use defaults in _prepare_ml_features and rule system)
    patient_data_7 = { 
        'Age': 50, 'Sex': 'female', 'BMI': 27.0, 'Smoking': 0, 'AlcoholConsumption': 10,
        # Missing ALT, AST, ALB, etc. to demonstrate default handling
        'HCV_RNA_Viral_Load': 0 
    }


    test_patients = {
        "Patient 1 (Low Risk)": patient_data_1,
        "Patient 2 (Moderate Risk / Potential HCV)": patient_data_2,
        "Patient 3 (High Risk / Confirmed HCV)": patient_data_3,
        "Patient 4 (Critical Risk / Severe Liver Damage, High Alcohol)": patient_data_4,
        "Patient 5 (Critical Risk / Severe Liver Damage, Low HCV)": patient_data_5,
        "Patient 6 (Critical Risk / Extremely High ALT)": patient_data_6,
        "Patient 7 (Missing Data Test)" : patient_data_7
    }

    for name, data in test_patients.items():
        print(f"\n--- Diagnosing {name} ---")
        diagnosis_results = predict_hepatitis_c(data) # Use the exposed function

        # Print the key diagnosis results clearly
        print(f"Hepatitis C Diagnosis (ML): {diagnosis_results.get('hepatitis_c_diagnosis_label', 'N/A')} (Probability: {diagnosis_results.get('ml_probability_hcv', 'N/A'):.2f})")
        print(f"Overall Liver Health Risk: {diagnosis_results.get('overall_health_risk_level', 'N/A')} (Score: {diagnosis_results.get('final_overall_risk_score', 'N/A'):.2f})")
        print(f"Decision Method for Overall Risk: {diagnosis_results.get('overall_decision_method', 'N/A')}")
            
        print("\n--- Detailed Interpretation ---")
        print("Contributing Factors/Evidence:")
        if diagnosis_results.get('overall_evidence'):
            for factor in diagnosis_results['overall_evidence']:
                print(f"   - {factor}")
        else:
            print("   No specific contributing factors identified or data was insufficient.")

        if diagnosis_results.get('is_critical_from_rules'):
            print("Critical Rule(s) Triggered! (This significantly influenced overall risk):")
            for crit_factor in diagnosis_results.get('critical_evidence', []):
                print(f"   - CRITICAL: {crit_factor}")
            
        print(f"\nRecommendation: {diagnosis_results.get('recommendation', 'N/A')}")
        print("\n" + "=" * 60 + "\n")