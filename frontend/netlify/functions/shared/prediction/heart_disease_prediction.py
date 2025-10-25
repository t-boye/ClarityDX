import logging
import numpy as np
import pandas as pd
from typing import Dict, Union, List, Tuple
from dataclasses import dataclass
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

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
class DiagnosticEvidence:
    factor: str
    value: Union[int, float, str]
    risk_contribution: float
    confidence: float
    reasoning: str

# --- Medical Knowledge Base ---
class HeartDiseaseKnowledgeBase:
    def __init__(self):
        self.risk_factors = self._initialize_risk_factors()
        self.normal_ranges = self._initialize_normal_ranges()
        self.feature_mapping = self._initialize_feature_mapping()
    
    def _initialize_risk_factors(self) -> Dict[str, Dict]:
        return {
            'age': {'ranges': [(0, 40, 0.1), (40, 55, 0.3), (55, 65, 0.5), (65, 75, 0.7), (75, 100, 0.9)], 'weight': 0.15},
            'sex': {'male': 0.6, 'female': 0.4, 'weight': 0.10},
            'cp': {'typical angina': 0.9, 'atypical angina': 0.6, 'non-anginal pain': 0.3, 'asymptomatic': 0.1, 'weight': 0.20},
            'trestbps': {'ranges': [(0, 120, 0.1), (120, 130, 0.3), (130, 140, 0.5), (140, 160, 0.7), (160, 250, 0.9)], 'weight': 0.15},
            'chol': {'ranges': [(0, 200, 0.2), (200, 240, 0.4), (240, 300, 0.7), (300, 500, 0.9)], 'weight': 0.15},
            'fbs': {'normal': 0.2, 'elevated': 0.8, 'weight': 0.10},
            'restecg': {'normal': 0.1, 'st-t abnormality': 0.5, 'left ventricular hypertrophy': 0.6, 'weight': 0.05},
            'thalach': {'ranges': [(0, 100, 0.8), (100, 140, 0.5), (140, 180, 0.2), (180, 220, 0.1)], 'weight': 0.10},
            'exang': {'no': 0.1, 'yes': 0.8, 'weight': 0.15},
            'oldpeak': {'ranges': [(0, 1.0, 0.1), (1.0, 2.0, 0.4), (2.0, 3.0, 0.7), (3.0, 7.0, 0.9)], 'weight': 0.20},
            'slope': {'upsloping': 0.2, 'flat': 0.5, 'downsloping': 0.8, 'weight': 0.18},
            'ca': {'ranges': [(0, 1, 0.1), (1, 2, 0.4), (2, 3, 0.7), (3, 4, 0.95)], 'weight': 0.25},
            'thal': {'normal': 0.1, 'reversible defect': 0.5, 'fixed defect': 0.9, 'weight': 0.22}
        }
    
    def _initialize_normal_ranges(self) -> Dict[str, Tuple[float, float]]:
        return {
            'age': (18, 100), 'trestbps': (70, 200), 'chol': (100, 400), 'thalach': (60, 220),
            'oldpeak': (0.0, 5.0), 'ca': (0, 3), 'fbs': (0, 1)
        }

    def _initialize_feature_mapping(self) -> Dict[str, Dict]:
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
        critical_flags = []
        max_risk_score = 0.0
        is_contradictory = False
        
        age = patient_data.get('age')
        cp = patient_data.get('cp')
        thalach = patient_data.get('thalach')
        exang = patient_data.get('exang')
        trestbps = patient_data.get('trestbps')
        oldpeak = patient_data.get('oldpeak')
        slope = patient_data.get('slope')
        ca = patient_data.get('ca')
        thal = patient_data.get('thal')

        # Critical Rules from your original code
        if ca is not None and ca >= 3:
            critical_flags.append("Severe multi-vessel coronary artery disease")
            max_risk_score = max(max_risk_score, 0.98) # Hardcoded from original rule
        if thal is not None and thal == 2:
            critical_flags.append("Fixed perfusion defect (previous MI)")
            max_risk_score = max(max_risk_score, 0.95)
        if oldpeak is not None and oldpeak > 2.5:
            critical_flags.append("Extreme ST depression during exercise")
            max_risk_score = max(max_risk_score, 0.92)
        if thalach is not None and thalach < 70 and (cp == 0 or exang == 1):
            critical_flags.append("Critically low Max Heart Rate with cardiac symptoms")
            max_risk_score = max(max_risk_score, 0.90)
        if trestbps is not None and trestbps < 70:
            critical_flags.append("Critically low Resting Blood Pressure")
            max_risk_score = max(max_risk_score, 0.90)

        # Contradiction Detection
        if (slope is not None and slope == 2 and ca is not None and ca == 0 and thal is not None and thal == 1):
            is_contradictory = True
            critical_flags.append("Conflicting results: Downsloping ST with no major vessel disease and normal perfusion scan.")
            max_risk_score = 0.5

        return len(critical_flags) > 0, critical_flags, max_risk_score, is_contradictory
    
    def calculate_risk_score(self, patient_data: Dict) -> Tuple[float, List[DiagnosticEvidence]]:
        evidence_list = []
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for factor_ml_name, config in self.kb.risk_factors.items():
            evidence = self._evaluate_risk_factor(factor_ml_name, patient_data, config)
            if evidence:
                evidence_list.append(evidence)
                if 'weight' in config:
                    total_weighted_score += evidence.risk_contribution * config['weight']
                    total_weight += config['weight']
        
        final_risk_score = total_weighted_score / total_weight if total_weight > 0 else 0.0
        return final_risk_score, evidence_list
    
    def _evaluate_risk_factor(self, factor_ml_name: str, patient_data: Dict, config: Dict) -> Union[DiagnosticEvidence, None]:
        try:
            value = patient_data.get(factor_ml_name)
            if value is None:
                return None
            
            risk_score = 0.0
            display_value = value
            reasoning = ""

            # Logic to evaluate ranges or categorical values
            if 'ranges' in config:
                for min_val, max_val, score in config['ranges']:
                    if min_val <= value < max_val:
                        risk_score = score
                        break
                reasoning = f"Value {value} is in range, contributing {risk_score:.2f} risk."
            elif isinstance(config, dict):
                # Reverse-map numerical values for display and lookup
                mapping = self.kb.feature_mapping.get(next(k for k,v in self.kb.feature_mapping.items() if v['ml_name'] == factor_ml_name), {}).get('mapping', {})
                reverse_mapping = {v: k for k, v in mapping.items()}
                
                # Special handling for sex
                if factor_ml_name == 'sex':
                    display_value = 'Male' if value == 1 else 'Female'
                    risk_score = config.get(display_value.lower(), 0.0)
                # General categorical handling
                else:
                    display_value = reverse_mapping.get(int(value), 'unknown')
                    risk_score = config.get(display_value.lower().replace(' ', '_'), 0.0)
                
                reasoning = f"Category '{display_value}' contributes {risk_score:.2f} risk."

            return DiagnosticEvidence(
                factor=factor_ml_name, value=display_value, risk_contribution=risk_score,
                confidence=config.get('confidence', 0.8), reasoning=reasoning
            )
        except Exception as e:
            logger.warning(f"Error evaluating {factor_ml_name}: {e}")
            return None


def _preprocess_user_input_for_ml(raw_data: Dict, models: Dict) -> Tuple[pd.DataFrame, List[str]]:
    """
    Preprocesses raw user input into a DataFrame ready for ML prediction pipeline.
    This includes mapping, validation, and aligning with expected feature names.
    """
    kb = HeartDiseaseKnowledgeBase()
    processed_data = {}
    validation_messages = []
    
    # Check for required artifacts
    if "heart_disease_feature_names" not in models:
        raise RuntimeError("Missing 'heart_disease_feature_names' in models dictionary.")
        
    feature_names = models["heart_disease_feature_names"]
    
    # Mapping from ML feature name back to user-friendly name for messages
    ml_to_user = {v['ml_name']: k for k, v in kb.feature_mapping.items()}
    
    for user_key, value in raw_data.items():
        config = kb.feature_mapping.get(user_key)
        if not config:
            logger.warning(f"Ignoring unknown input key: {user_key}")
            continue

        ml_key = config['ml_name']

        if "mapping" in config:
            # Handle string or numerical categorical inputs
            mapped_value = config["mapping"].get(value)
            if mapped_value is None:
                # Check if the user provided the numeric value directly
                try:
                    mapped_value = int(value)
                    if mapped_value not in config["mapping"].values():
                        raise ValueError
                except (ValueError, TypeError):
                    raise ValueError(f"Invalid value for '{user_key}': '{value}'. Expected one of {list(config['mapping'].keys())} or their corresponding numeric codes.")
            processed_data[ml_key] = float(mapped_value)
        else:
            # Handle numerical inputs
            try:
                numeric_value = float(value)
                processed_data[ml_key] = numeric_value
            except (ValueError, TypeError):
                raise ValueError(f"Invalid numerical input for '{user_key}': '{value}'. Must be a number.")
        
        # Physiological validation
        normal_range = kb.normal_ranges.get(ml_key)
        if normal_range and ml_key in processed_data:
            min_val, max_val = normal_range
            if not (min_val <= processed_data[ml_key] <= max_val):
                msg = f"'{user_key}' ({value}) is outside the normal physiological range ({min_val}-{max_val})."
                validation_messages.append(msg)
    
    # Create DataFrame and align columns with the model's feature names
    df = pd.DataFrame([processed_data])
    df = df.reindex(columns=feature_names, fill_value=0.0)
    
    return df, validation_messages


def _predict_heart_disease_ml_only(processed_data: pd.DataFrame, models: Dict) -> Dict:
    """
    Performs the Machine Learning prediction using the loaded model pipeline.
    """
    model = models.get("heart_disease_model")
    scaler = models.get("heart_disease_scaler")
    poly_features = models.get("heart_disease_polynomial_features")
    pca = models.get("heart_disease_pca")

    if None in [model, scaler, poly_features, pca]:
        logger.error("Heart Disease ML model components are not loaded.")
        return {"prediction": "N/A", "probability": "N/A", "ml_status": "Failed", "details": "ML model components not available."}
    
    try:
        # Preprocessing pipeline
        scaled_data = scaler.transform(processed_data)
        poly_data = poly_features.transform(scaled_data)
        pca_data = pca.transform(poly_data)

        # The model expects a batch, so ensure the input has the correct shape
        input_array = pca_data.astype(np.float32)
        
        # Make prediction
        predictions = model.predict(input_array)
        probability_of_disease = float(predictions[0][0])
        prediction_class = 1 if probability_of_disease >= 0.5 else 0

        logger.info(f"Heart Disease ML prediction: Class={prediction_class}, Probability={probability_of_disease:.4f}")

        return {
            "prediction": "Positive" if prediction_class == 1 else "Negative",
            "probability": probability_of_disease,
            "ml_status": "Success",
            "details": f"ML model predicted disease with {probability_of_disease:.2%} confidence."
        }
    except Exception as e:
        logger.error(f"Error during Heart Disease ML-only prediction: {e}", exc_info=True)
        return {"prediction": "N/A", "probability": "N/A", "ml_status": "Failed", "details": f"ML prediction failed: {str(e)}"}


def predict_heart_disease(raw_user_data: Dict, models: Dict) -> Dict:
    """
    Combines rule-based logic and ML prediction for a comprehensive heart disease diagnosis.
    
    Args:
        raw_user_data (Dict): Raw patient input received from the API request.
        models (Dict): A dictionary containing all pre-loaded model artifacts.
    
    Returns:
        Dict: A dictionary containing the diagnosis, risk level, and explanations.
    """
    kb = HeartDiseaseKnowledgeBase()
    rule_based_system = RuleBasedDiagnosticSystem(kb)
    
    diagnosis_results = {
        "diagnosis": "Uncertain",
        "risk_level": RiskLevel.INDETERMINATE.value,
        "ml_prediction": "N/A",
        "ml_probability": "N/A",
        "rule_based_evidence": [],
        "explanations": [],
        "critical_flags": [],
        "recommendations": [],
        "warnings": [],
        "medical_disclaimer": "This is a prediction, not a definitive diagnosis. Consult a healthcare professional."
    }

    try:
        # Step 1: Preprocess user input and get a DataFrame for the ML model
        processed_ml_df, validation_warnings = _preprocess_user_input_for_ml(raw_user_data, models)
        diagnosis_results["warnings"].extend(validation_warnings)
        
        # Step 2: Perform the Rule-Based evaluation
        rule_based_risk_score, evidence_list = rule_based_system.calculate_risk_score(processed_ml_df.iloc[0].to_dict())
        is_critical, critical_reasons, critical_risk_score, is_contradictory = rule_based_system.evaluate_critical_rules(processed_ml_df.iloc[0].to_dict())
        
        diagnosis_results["rule_based_risk_score"] = rule_based_risk_score
        diagnosis_results["rule_based_evidence"] = [ev.__dict__ for ev in evidence_list]
        diagnosis_results["critical_flags"] = critical_reasons
        diagnosis_results["contradiction_detected"] = is_contradictory
        
        # Step 3: Perform the ML prediction
        ml_result = _predict_heart_disease_ml_only(processed_ml_df, models)
        diagnosis_results["ml_prediction"] = ml_result.get("prediction")
        diagnosis_results["ml_probability"] = ml_result.get("probability")
        
        # Step 4: Combine results for a final diagnosis and risk level
        final_risk_score = (rule_based_risk_score + float(ml_result.get("probability", 0))) / 2
        
        if is_critical or is_contradictory:
            final_risk_score = max(final_risk_score, critical_risk_score)
            diagnosis_results["risk_level"] = RiskLevel.CRITICAL.value if is_critical else RiskLevel.INDETERMINATE.value
        elif final_risk_score > 0.85:
            diagnosis_results["risk_level"] = RiskLevel.HIGH.value
        elif final_risk_score > 0.6:
            diagnosis_results["risk_level"] = RiskLevel.MODERATE.value
        elif final_risk_score > 0.3:
            diagnosis_results["risk_level"] = RiskLevel.LOW.value
        else:
            diagnosis_results["risk_level"] = RiskLevel.VERY_LOW.value

        # Determine final diagnosis message
        if diagnosis_results["risk_level"] in [RiskLevel.HIGH.value, RiskLevel.CRITICAL.value, RiskLevel.INDETERMINATE.value]:
            diagnosis_results["diagnosis"] = "High likelihood of Heart Disease detected."
            diagnosis_results["recommendations"].append("Consult a cardiologist for a comprehensive evaluation.")
            if is_critical:
                diagnosis_results["recommendations"].append("URGENT: Immediate medical attention required due to critical risk factors identified.")
        else:
            diagnosis_results["diagnosis"] = "Low likelihood of Heart Disease detected."
            diagnosis_results["recommendations"].append("Continue monitoring and consider a routine checkup.")

        # Add all relevant factors to explanations
        diagnosis_results["explanations"].append(f"Final combined risk score: {final_risk_score:.2f}")
        diagnosis_results["explanations"].append(f"Machine Learning model probability: {diagnosis_results['ml_probability']:.2%}")
        diagnosis_results["explanations"].append(f"Rule-based risk score: {diagnosis_results['rule_based_risk_score']:.2f}")
        
    except Exception as e:
        logger.exception(f"An unexpected error occurred during heart disease prediction: {e}")
        diagnosis_results["diagnosis"] = "Processing Error"
        diagnosis_results["risk_level"] = RiskLevel.INDETERMINATE.value
        diagnosis_results["warnings"].append(f"An internal error occurred: {str(e)}")

    return diagnosis_results