import os
import joblib
import numpy as np
import pandas as pd
import logging
from typing import Dict, Union, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import tempfile

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # Set to DEBUG for verbose output during debugging
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# --- Risk Level Enum (Copied for consistency, if not global) ---
class RiskLevel(Enum):
    VERY_LOW = "Very Low Risk"
    LOW = "Low Risk"
    MODERATE = "Moderate Risk"
    HIGH = "High Risk"
    CRITICAL = "Critical Risk"

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
    risk_contribution: float # How much this factor itself contributes to risk (0-1)
    confidence: float # Confidence in this piece of evidence (e.g., based on data quality, clinical certainty)
    reasoning: str # Explains *why* this is evidence

# --- Hepatitis C Specific Medical Knowledge Base ---
class HepatitisCKnowledgeBase:
    def __init__(self):
        self.rules = self._initialize_medical_rules()
        self.risk_factors = self._initialize_risk_factors()
        self.normal_ranges = self._initialize_normal_ranges()
        
    def _initialize_medical_rules(self) -> List[MedicalRule]:
        """
        Initialize comprehensive medical rules based on Hepatitis C guidelines.
        """
        return [
            # Critical Risk Rules for Hepatitis C
            MedicalRule(
                condition="fibrosis_cirrhosis",
                risk_score=0.98,
                evidence_weight=0.95,
                description="Evidence of advanced liver fibrosis or cirrhosis (e.g., high AST/ALT, high GGT, low ALB)",
                recommendation="URGENT: Immediate hepatology consultation for advanced liver disease management"
            ),
            MedicalRule(
                condition="high_viral_load_symptoms",
                risk_score=0.90,
                evidence_weight=0.85,
                description="High viral load combined with significant symptoms (e.g., jaundice, ascites)",
                recommendation="URGENT: Initiate antiviral therapy immediately, symptomatic management"
            ),
            MedicalRule(
                condition="persisted_elevated_enzymes",
                risk_score=0.85,
                evidence_weight=0.80,
                description="Persistently elevated liver enzymes (ALT/AST) over 6 months, indicating chronic infection",
                recommendation="Confirm chronic infection, evaluate for antiviral treatment"
            ),
            
            # High Risk Rules
            MedicalRule(
                condition="moderate_fibrosis",
                risk_score=0.75,
                evidence_weight=0.70,
                description="Signs of moderate liver fibrosis (e.g., abnormal AST/ALT, GGT)",
                recommendation="Liver biopsy or non-invasive fibrosis assessment recommended"
            ),
            MedicalRule(
                condition="multiple_abnormal_markers",
                risk_score=0.70,
                evidence_weight=0.65,
                description="Multiple abnormal liver function tests (e.g., elevated ALT, AST, GGT, BIL)",
                recommendation="Comprehensive liver workup and viral serology"
            ),
            
            # Moderate Risk Rules
            MedicalRule(
                condition="elevated_alt_ast",
                risk_score=0.55,
                evidence_weight=0.50,
                description="Elevated ALT and/or AST levels without other severe signs",
                recommendation="Monitor liver function, investigate potential causes (viral, fatty liver, etc.)"
            )
        ]
    
    def _initialize_risk_factors(self) -> Dict[str, Dict]:
        """Initialize risk factor scoring system for Hepatitis C."""
        return {
            'Age': { # Using 'Age' to match input data key
                'ranges': [(0, 30, 0.1), (30, 50, 0.3), (50, 65, 0.6), (65, 100, 0.8)],
                'weight': 0.15
            },
            'Sex': { # Using 'Sex' to match input data key
                'male': 0.55, 'female': 0.45,
                'weight': 0.05
            },
            'ALB': { # Albumin (low indicates liver dysfunction)
                'ranges': [(0, 3.5, 0.8), (3.5, 4.5, 0.2), (4.5, 6.0, 0.1)],
                'weight': 0.10
            },
            'ALP': { # Alkaline Phosphatase (elevated in bile duct obstruction)
                'ranges': [(0, 40, 0.1), (40, 120, 0.2), (120, 200, 0.5), (200, 1000, 0.8)],
                'weight': 0.08
            },
            'ALT': { # Alanine Aminotransferase (liver inflammation)
                'ranges': [(0, 40, 0.1), (40, 80, 0.4), (80, 200, 0.7), (200, 1000, 0.9)],
                'weight': 0.12
            },
            'AST': { # Aspartate Aminotransferase (liver damage)
                'ranges': [(0, 40, 0.1), (40, 80, 0.4), (80, 200, 0.7), (200, 1000, 0.9)],
                'weight': 0.12
            },
            'BIL': { # Bilirubin (jaundice, liver dysfunction)
                'ranges': [(0, 1.2, 0.1), (1.2, 3.0, 0.5), (3.0, 10.0, 0.8), (10.0, 50.0, 0.9)],
                'weight': 0.09
            },
            'CHE': { # Cholinesterase (synthesized by liver, decreased in liver disease)
                'ranges': [(0, 4000, 0.8), (4000, 12000, 0.2)],
                'weight': 0.07
            },
            'CHOL': { # Cholesterol (can be affected by liver disease)
                'ranges': [(0, 150, 0.4), (150, 240, 0.2), (240, 500, 0.6)],
                'weight': 0.06
            },
            'CREA': { # Creatinine (kidney function, can be affected by advanced liver disease)
                'ranges': [(0, 1.2, 0.1), (1.2, 2.0, 0.5), (2.0, 10.0, 0.8)],
                'weight': 0.07
            },
            'GGT': { # Gamma-Glutamyl Transferase (bile duct, liver damage)
                'ranges': [(0, 50, 0.1), (50, 150, 0.4), (150, 500, 0.7), (500, 2000, 0.9)],
                'weight': 0.11
            },
            'PROT': { # Total Protein (overall liver function)
                'ranges': [(0, 6.0, 0.8), (6.0, 8.0, 0.2), (8.0, 10.0, 0.1)],
                'weight': 0.08
            },
            'AST_ALT': { # AST/ALT Ratio (indicator of liver damage type)
                'ranges': [(0, 0.8, 0.2), (0.8, 1.5, 0.5), (1.5, 5.0, 0.8)],
                'weight': 0.09
            }
        }
    
    def _initialize_normal_ranges(self) -> Dict[str, Tuple[float, float]]:
        """Define normal physiological ranges for Hepatitis C related parameters."""
        return {
            'ALB': (3.5, 5.5), 'ALP': (40, 120), 'ALT': (7, 56), 'AST': (8, 48), 
            'BIL': (0.1, 1.2), 'CHE': (5300, 12900), 'CHOL': (125, 200), 'CREA': (0.7, 1.2),
            'GGT': (9, 48), 'PROT': (6.0, 8.3), 'AST_ALT': (0.8, 1.5)
        }

# --- Rule-Based Diagnostic System for Hepatitis C ---
class HepatitisCRuleBasedSystem:
    def __init__(self, knowledge_base: HepatitisCKnowledgeBase):
        self.kb = knowledge_base
        
    def evaluate_critical_rules(self, patient_data: Dict) -> Tuple[bool, List[str], List[str], float]:
        """
        Evaluates patient data against predefined critical rules for Hepatitis C.
        These rules can indicate severe conditions that might override ML predictions.
        Returns: (is_critical, critical_flags_list, critical_evidence_list, max_risk_score)
        """
        critical_flags = []
        critical_evidence = [] # To store detailed evidence for critical flags
        max_risk_score = 0.0
        
        logger.debug("--- Evaluating Hepatitis C Critical Rules ---")

        # Rule 1: Fibrosis/Cirrhosis indicators
        ast_alt_ratio = patient_data.get('AST_ALT', 0.0)
        alb = patient_data.get('ALB', 0.0)
        ggt = patient_data.get('GGT', 0.0)
        
        # Get normal ranges for evidence generation
        normal_alb_min, normal_alb_max = self.kb.normal_ranges.get('ALB', (3.5, 5.5))
        normal_ggt_min, normal_ggt_max = self.kb.normal_ranges.get('GGT', (9, 48))
        normal_ast_alt_min, normal_ast_alt_max = self.kb.normal_ranges.get('AST_ALT', (0.8, 1.5))


        if (ast_alt_ratio >= 1.5 and alb < 3.0) or (ggt > 200 and alb < 3.0):
            critical_flags.append("Advanced Liver Fibrosis/Cirrhosis Markers")
            evidence_str = "Indicators of advanced liver disease: "
            if ast_alt_ratio >= 1.5:
                evidence_str += f"Elevated AST/ALT Ratio ({ast_alt_ratio:.2f} > {normal_ast_alt_max:.2f}). "
            if alb < 3.0:
                evidence_str += f"Significantly low Albumin ({alb} < {normal_alb_min}). "
            if ggt > 200:
                evidence_str += f"Highly elevated GGT ({ggt} > {normal_ggt_max})."
            critical_evidence.append(evidence_str.strip())
            max_risk_score = max(max_risk_score, 0.98)
            logger.debug(f"  CRITICAL Rule 1 Triggered: Fibrosis/Cirrhosis (AST/ALT={ast_alt_ratio}, ALB={alb}, GGT={ggt})")

        # Rule 2: Persisted Elevated Enzymes (Inferred from high current values)
        alt = patient_data.get('ALT', 0.0)
        ast = patient_data.get('AST', 0.0)
        
        normal_alt_min, normal_alt_max = self.kb.normal_ranges.get('ALT', (7, 56))
        normal_ast_min, normal_ast_max = self.kb.normal_ranges.get('AST', (8, 48))

        # This rule typically requires historical data to confirm 'persisted',
        # but for a single snapshot, we can infer high elevation indicating a severe state.
        if alt > 3 * normal_alt_max or ast > 3 * normal_ast_max: # e.g., ALT > 168 or AST > 144
            critical_flags.append("Severely Elevated Liver Enzymes")
            evidence_str = "Severely high liver enzymes: "
            if alt > 3 * normal_alt_max:
                evidence_str += f"ALT ({alt} > {3 * normal_alt_max:.2f}). "
            if ast > 3 * normal_ast_max:
                evidence_str += f"AST ({ast} > {3 * normal_ast_max:.2f})."
            critical_evidence.append(evidence_str.strip())
            max_risk_score = max(max_risk_score, 0.85) 
            logger.debug(f"  CRITICAL Rule 2 Triggered: Severely elevated enzymes (ALT={alt}, AST={ast})")

        # Rule 3: Multiple severe abnormalities
        severe_abnormalities = []
        bil = patient_data.get('BIL', 0.0)
        crea = patient_data.get('CREA', 0.0)
        alb_for_rule3 = patient_data.get('ALB', 0.0) # Use a different var to avoid conflict with rule 1 check

        normal_bil_min, normal_bil_max = self.kb.normal_ranges.get('BIL', (0.1, 1.2))
        normal_crea_min, normal_crea_max = self.kb.normal_ranges.get('CREA', (0.7, 1.2))

        if bil > 3.0 * normal_bil_max: # Significantly high bilirubin (jaundice)
            severe_abnormalities.append(f"Highly elevated Bilirubin ({bil:.2f} > {3 * normal_bil_max:.2f})")
        if crea > 2.0 * normal_crea_max: # Significantly impaired kidney function
            severe_abnormalities.append(f"Elevated Creatinine ({crea:.2f} > {2 * normal_crea_max:.2f})")
        if alb_for_rule3 < 2.5: # Very low albumin
            severe_abnormalities.append(f"Very low Albumin ({alb_for_rule3:.2f} < 2.5)")
        
        if len(severe_abnormalities) >= 2:
            critical_flags.append(f"Multiple Severe Liver-Related Abnormalities ({len(severe_abnormalities)})")
            critical_evidence.append("Combined severe abnormalities: " + "; ".join(severe_abnormalities))
            max_risk_score = max(max_risk_score, 0.90)
            logger.debug(f"  CRITICAL Rule 3 Triggered: Multiple severe abnormalities ({len(severe_abnormalities)})")

        logger.debug(f"  Critical flags detected: {critical_flags}, Critical Evidence: {critical_evidence}, Max Critical Risk Score: {max_risk_score:.3f}")
        return len(critical_flags) > 0, critical_flags, critical_evidence, max_risk_score # MODIFIED RETURN
    
    def calculate_risk_score(self, patient_data: Dict) -> Tuple[float, List[DiagnosticEvidence]]:
        """
        Calculate comprehensive risk score for Hepatitis C using rule-based system.
        """
        evidence_list = []
        total_weighted_score = 0.0
        total_weight = 0.0
        
        logger.debug("--- Calculating Hepatitis C Rule-Based Risk Score ---")
        
        # Check for essential missing data upfront to return None early
        # For simplicity, let's assume 'AST_ALT' and 'ALB' are essential for core rule calculation
        # You can expand this check based on what truly makes the rule system inoperable.
        if 'AST_ALT' not in patient_data or 'ALB' not in patient_data:
            logger.error("Essential patient data (e.g., AST_ALT, ALB) for rule-based score calculation is missing.")
            return None # Return None if essential data for rule-based system is missing

        for factor, config in self.kb.risk_factors.items():
            evidence = self._evaluate_risk_factor(factor, patient_data, config)
            if evidence:
                evidence_list.append(evidence)
                total_weighted_score += evidence.risk_contribution * config['weight']
                total_weight += config['weight']
                logger.debug(f"  Factor '{factor}': Value={evidence.value}, Contribution={evidence.risk_contribution:.2f}, Weight={config['weight']:.2f}, Weighted Score={evidence.risk_contribution * config['weight']:.2f}")
            else:
                # If a non-essential factor is missing, we can still proceed
                # but might want to log a warning or adjust total_weight if the factor was intended to contribute.
                # If it's a truly essential factor for the *overall* score calculation, you might consider returning None here too.
                logger.debug(f"  Factor '{factor}' missing in patient data or not evaluated. Skipping its contribution to score.")
                continue # Continue to the next factor if one is missing but not critical for the whole score.

        final_risk_score = total_weighted_score / total_weight if total_weight > 0 else 0.0
        logger.debug(f"Total Weighted Score: {total_weighted_score:.3f}, Total Weight: {total_weight:.3f}")
        logger.debug(f"Rule-based final risk score: {final_risk_score:.3f}")
        logger.debug(f"Rule-based evidence collected: {evidence_list}")
        
        return final_risk_score, evidence_list
    
    def _evaluate_risk_factor(self, factor: str, patient_data: Dict, config: Dict) -> Optional[DiagnosticEvidence]:
        """Evaluates individual risk factor for Hepatitis C and returns DiagnosticEvidence."""
        try:
            val = patient_data.get(factor)
            if val is None:
                logger.debug(f"  Factor '{factor}' missing in patient data. Skipping rule evaluation for this factor.")
                return None

            if 'ranges' in config: # Numerical factors with ranges
                risk_score = self._evaluate_ranges(val, config['ranges'])
                normal_min, normal_max = self.kb.normal_ranges.get(factor, (float('-inf'), float('inf')))
                
                reasoning = f"{factor} value {val:.2f} is "
                if val < normal_min:
                    reasoning += f"below normal range ({normal_min:.2f}-{normal_max:.2f})"
                elif val > normal_max:
                    reasoning += f"above normal range ({normal_min:.2f}-{normal_max:.2f})"
                else:
                    reasoning += f"within normal range ({normal_min:.2f}-{normal_max:.2f})"
                reasoning += f", contributing {risk_score:.2f} to risk."

                return DiagnosticEvidence(
                    factor=factor, value=val, risk_contribution=risk_score, confidence=0.9,
                    reasoning=reasoning
                )
            elif factor == 'Sex': # Categorical 'Sex'
                # Convert numerical sex (0 or 1) to 'female' or 'male' string for lookup
                str_val = 'male' if val == 1 else 'female'
                risk_score = config.get(str_val, 0.0)
                return DiagnosticEvidence(
                    factor=factor, value=str_val, risk_contribution=risk_score, confidence=0.7,
                    reasoning=f"Sex '{str_val}' contributes {risk_score:.2f} to risk."
                )
            elif factor == 'Age': # Age handling (already has ranges)
                risk_score = self._evaluate_ranges(val, config['ranges'])
                return DiagnosticEvidence(
                    factor=factor, value=val, risk_contribution=risk_score, confidence=0.8,
                    reasoning=f"Age {val} falls into a group contributing {risk_score:.2f} to risk."
                )
            else:
                # Fallback for other types or unhandled factors
                logger.debug(f"  Factor '{factor}' with value '{val}' not explicitly handled by specific rule logic.")
                return None
            
        except Exception as e:
            logger.warning(f"Error evaluating {factor}: {e}")
            return None
    
    def _evaluate_ranges(self, value: float, ranges: List[Tuple]) -> float:
        """Evaluates a numerical value against defined ranges."""
        for min_val, max_val, risk_score in ranges:
            if min_val <= value < max_val:
                return risk_score
        return ranges[-1][2] # Default to highest risk if value exceeds all ranges

# --- Enhanced Prediction System for Hepatitis C ---
class EnhancedHepatitisCDiagnosticSystem:
    def __init__(self):
        self.knowledge_base = HepatitisCKnowledgeBase()
        self.rule_system = HepatitisCRuleBasedSystem(self.knowledge_base)
        
    def predict_with_hybrid_approach(self, raw_data: Dict) -> Dict:
        """Hybrid prediction using ML + Rule-based + Knowledge-based approach for Hepatitis C."""
        logger.debug("--- Starting Enhanced Hepatitis C Prediction with Hybrid Approach ---")
        logger.debug(f"Raw data received by EnhancedSystem: {raw_data}")
        
        # Initialize variables that might not be set if a branch is skipped
        rule_risk_score = 0.0
        general_evidence_list = []
        ml_risk_score = 0.0
        ml_prediction_class = 0
        final_risk = 0.0
        final_class = 0
        decision_method = "Unknown"
        recommendation = "No specific recommendation due to insufficient data or error."
        final_evidence_for_output = []
        final_critical_flags_for_output = []
        rule_score_display = 0.0 # Variable to hold the actual rule score or a descriptive string

        try:
            # Step 1: Rule-based critical evaluation (highest priority)
            is_critical, critical_reasons_summary, critical_evidence_detailed, critical_risk = self.rule_system.evaluate_critical_rules(raw_data) 
            logger.debug(f"Critical Evaluation Results: is_critical={is_critical}, critical_reasons_summary={critical_reasons_summary}, critical_evidence_detailed={critical_evidence_detailed}, critical_risk={critical_risk:.3f}")
            
            # Step 2: Calculate rule-based risk score for general evidence and interpretation
            rule_system_result = self.rule_system.calculate_risk_score(raw_data)
            
            if rule_system_result is None:
                logger.warning("Essential patient data for rule-based score calculation is missing. Falling back to ML-only prediction if possible.")
                rule_score_display = "N/A (Missing essential data)" # Set display string
                
                # If rule_based_score cannot be calculated, proceed with ML only
                ml_result = self._get_ml_prediction(raw_data)
                if 'error' in ml_result:
                    logger.error(f"ML prediction also failed: {ml_result['details']}")
                    raise RuntimeError(ml_result['details'])

                ml_risk_score = ml_result.get('probability_class_1', 0.5)
                ml_prediction_class = ml_result.get('prediction_class', 0)

                final_risk = ml_risk_score # Use ML score as final risk
                final_class = ml_prediction_class
                decision_method = "ML-only (Rule-based data missing)"
                recommendation = self._get_risk_based_recommendation(final_risk, []) # No rule evidence for general
                final_evidence_for_output = ["ML prediction made due to missing rule-based data for rule-based score calculation."]
                # Still include critical flags if found, even if rule score couldn't be calculated
                if is_critical:
                    final_critical_flags_for_output.extend(critical_reasons_summary) 
                    # If it's critical, prediction class should be 1, and risk should be high
                    final_class = 1 
                    final_risk = max(final_risk, critical_risk) # Ensure high risk if critical
                    recommendation = self._get_critical_recommendation(critical_reasons_summary)
                    final_evidence_for_output.extend(critical_evidence_detailed)

            else:
                rule_risk_score, general_evidence_list = rule_system_result
                rule_score_display = float(rule_risk_score) # Set display to float value
                logger.debug(f"Rule-based Risk Score: {rule_risk_score:.3f}")
                
                # Step 3: Get ML prediction
                ml_result = self._get_ml_prediction(raw_data)
                if 'error' in ml_result:
                    logger.error(f"ML prediction failed: {ml_result['details']}")
                    raise RuntimeError(ml_result['details'])

                ml_risk_score = ml_result.get('probability_class_1', 0.5) # Assuming class 1 is "Hepatitis C" or disease presence
                ml_prediction_class = ml_result.get('prediction_class', 0)
                logger.debug(f"ML Risk Score (from _get_ml_prediction): {ml_risk_score:.3f}, ML Class: {ml_prediction_class}")
                
                # Step 4: Hybrid decision making
                if is_critical:
                    final_risk = critical_risk
                    final_class = 1 # Critical conditions always imply Hepatitis C Detected
                    decision_method = "Rule-based override (Critical)"
                    recommendation = self._get_critical_recommendation(critical_reasons_summary)
                    
                    # Prioritize critical detailed evidence, then add general evidence not already captured
                    final_evidence_for_output.extend(critical_evidence_detailed)
                    for ev in general_evidence_list:
                        if ev.reasoning not in final_evidence_for_output: # Avoid duplicates
                            final_evidence_for_output.append(ev.reasoning)
                    
                    final_critical_flags_for_output.extend(critical_reasons_summary) # Populate critical flags
                    
                    logger.info(f"Critical override applied. Final risk: {final_risk:.3f}, Final Class: {final_class}")
                else:
                    ml_weight = 0.6  # Adjust based on your ML model's reliability
                    rule_weight = 0.4
                    
                    final_risk = (ml_risk_score * ml_weight) + (rule_risk_score * rule_weight)
                    final_class = 1 if final_risk > 0.5 else 0 # Determine final class based on combined risk
                    decision_method = "Hybrid ML + Rule-based"
                    recommendation = self._get_risk_based_recommendation(final_risk, general_evidence_list)
                    final_evidence_for_output = [ev.reasoning for ev in general_evidence_list] # Use only general evidence
                    # critical_flags remains empty if not critical
                    
                    logger.info(f"Hybrid decision applied. ML Weighted: {ml_risk_score * ml_weight:.3f}, Rule Weighted: {rule_risk_score * rule_weight:.3f}. Final risk: {final_risk:.3f}, Final Class: {final_class}")
            
            # Step 5: Determine risk level
            risk_level = self._determine_risk_level(final_risk)
            logger.debug(f"Determined Risk Level: {risk_level.value}")
            
            return {
                "diagnosis": self._format_diagnosis(final_class, risk_level),
                "probability": float(final_risk),
                "prediction_class": final_class,
                "risk_level": risk_level.value,
                "decision_method": decision_method,
                "interpretation": {
                    "recommendation": recommendation,
                    # Ensure evidence is the properly populated list
                    "evidence": final_evidence_for_output, 
                    "ml_score": float(ml_risk_score), 
                    "rule_score": rule_score_display, # Use the potentially string value here
                    # Ensure critical_flags is the properly populated list
                    "critical_flags": final_critical_flags_for_output, 
                    "probability_breakdown": [
                        {"class": "No Hepatitis C", "probability": float(1 - final_risk)},
                        {"class": "Hepatitis C", "probability": float(final_risk)}
                    ],
                    "disclaimer": (
                        "This diagnosis combines machine learning with clinical rule-based analysis. "
                        "It should not replace professional medical advice. Always consult with a "
                        "qualified healthcare provider for definitive diagnosis and treatment."
                    )
                }
            }
            
        except Exception as e:
            logger.error(f"Error in enhanced prediction: {e}", exc_info=True)
            return {"error": "Prediction failed", "details": str(e)}
    
    def _get_ml_prediction(self, raw_data: Dict) -> Dict:
        """Wrapper to get prediction from the ML model."""
        # Ensure 'Sex' is passed as 0 or 1 to _predict_hepatitis_c_ml_only
        processed_ml_data = preprocess_user_input_for_ml_hepatitis_c(raw_data)
        return _predict_hepatitis_c_ml_only(processed_ml_data) # Calls the ML-only prediction function
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level based on score."""
        if risk_score >= 0.8: return RiskLevel.CRITICAL
        elif risk_score >= 0.6: return RiskLevel.HIGH
        elif risk_score >= 0.4: return RiskLevel.MODERATE
        elif risk_score >= 0.2: return RiskLevel.LOW
        else: return RiskLevel.VERY_LOW
    
    def _format_diagnosis(self, prediction_class: int, risk_level: RiskLevel) -> str:
        """Format diagnosis string."""
        if prediction_class == 1: return f"Hepatitis C Detected ({risk_level.value})"
        else: return f"No Hepatitis C Detected ({risk_level.value})"
    
    def _get_critical_recommendation(self, critical_reasons: List[str]) -> str:
        """Get recommendation for critical cases."""
        # Join reasons with a comma for a readable string
        return (
            f"🚨 CRITICAL: Immediate hepatology consultation required. "
            f"Critical factors detected: {', '.join(critical_reasons)}. "
            f"This patient requires urgent evaluation and likely intervention."
        )
    
    def _get_risk_based_recommendation(self, risk_score: float, evidence: List[DiagnosticEvidence]) -> str:
        """Get recommendation based on risk score and evidence."""
        # Note: 'evidence' here is the list of DiagnosticEvidence objects,
        # which can be used to tailor recommendations further if needed.
        # For now, we'll use the existing text.
        if risk_score >= 0.7:
            return (
                "HIGH RISK: Urgent hepatology referral recommended. "
                "Consider viral load testing, liver elastography, and possible biopsy. "
                "Immediate lifestyle modifications and medical management indicated."
            )
        elif risk_score >= 0.5:
            return (
                "MODERATE RISK: Hepatology consultation recommended within 2-4 weeks. "
                "Consider comprehensive liver function tests and fibrosis assessment. "
                "Implement lifestyle modifications and monitor closely."
            )
        elif risk_score >= 0.3:
            return (
                "LOW-MODERATE RISK: Primary care follow-up with liver function assessment. "
                "Consider lifestyle counseling and risk factor modification. "
                "Routine monitoring recommended."
            )
        else:
            return (
                "LOW RISK: Continue routine preventive care. "
                "Maintain healthy lifestyle. "
                "Annual liver function screening appropriate."
            )

# --- Directory Paths ---
CURRENT_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_BASE_DIR = os.path.join(CURRENT_SCRIPT_DIR, "models")
HEPATITIS_C_MODEL_DIR = os.path.join(MODELS_BASE_DIR, "hepatitis_c_model_advanced")

# Model artifact paths
HEPATITIS_C_MODEL_PATH = os.path.join(HEPATITIS_C_MODEL_DIR, "hepatitis_c_model_advanced.keras")
HEPATITIS_C_SCALER_PATH = os.path.join(HEPATITIS_C_MODEL_DIR, "hepatitis_c_scaler.pkl")
HEPATITIS_C_FEATURE_NAMES_PATH = os.path.join(HEPATITIS_C_MODEL_DIR, "hepatitis_c_feature_names.pkl")

# Global artifact instances
hepatitis_c_model_instance = None
hepatitis_c_scaler_instance = None
hepatitis_c_feature_names_list = None

def load_hepatitis_c_artifacts():
    """
    Loads pre-trained ML model artifacts for Hepatitis C.
    Creates dummy artifacts if files are not found.
    """
    global hepatitis_c_model_instance
    global hepatitis_c_scaler_instance
    global hepatitis_c_feature_names_list

    try:
        try:
            from tensorflow.keras.models import load_model as keras_load_model
            from tensorflow import keras
        except ImportError:
            raise RuntimeError("TensorFlow is not installed. Please install it using 'pip install tensorflow' to enable ML predictions.")

        os.makedirs(HEPATITIS_C_MODEL_DIR, exist_ok=True)

        if hepatitis_c_model_instance is None:
            if not os.path.exists(HEPATITIS_C_MODEL_PATH):
                logger.warning(f"Hepatitis C Model file not found: {HEPATITIS_C_MODEL_PATH}. Creating mock Keras model.")
                # The Hepatitis C model usually predicts one of 4 classes (0, 1, 2, 3) + control.
                # Assuming 13 features ('Age', 'Sex', 'ALB', 'ALP', 'ALT', 'AST', 'BIL', 'CHE', 'CHOL', 'CREA', 'GGT', 'PROT', 'AST_ALT')
                # These are the *raw* features that will be scaled.
                # If your model expects AgeGroup_Middle and AgeGroup_Old as separate features, input_shape needs to be 15.
                # Let's assume the ML model expects the 13 base features for simplicity in this dummy.
                dummy_model = keras.Sequential([
                    keras.layers.Input(shape=(13,)), # Input layer, matches number of features in feature_names_list
                    keras.layers.Dense(32, activation='relu'),
                    keras.layers.Dense(4, activation='softmax') # 4 classes for Hepatitis C (e.g., 0, 1, 2, 3)
                ])
                dummy_model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')
                dummy_model.save(HEPATITIS_C_MODEL_PATH)
                logger.warning("Created a dummy Keras model for Hepatitis C testing purposes.")
            hepatitis_c_model_instance = keras_load_model(HEPATITIS_C_MODEL_PATH)
            logger.info(f"Loaded Hepatitis C Keras Model from: {HEPATITIS_C_MODEL_PATH}")

        if hepatitis_c_scaler_instance is None:
            if not os.path.exists(HEPATITIS_C_SCALER_PATH):
                logger.warning(f"Hepatitis C Scaler file not found: {HEPATITIS_C_SCALER_PATH}. Creating mock Scaler.")
                from sklearn.preprocessing import StandardScaler
                # Fit on dummy data with expected number of features (e.g., 13 features)
                dummy_scaler = StandardScaler()
                # Ensure dummy data matches the expected feature count
                dummy_scaler.fit(np.random.rand(100, 13)) 
                joblib.dump(dummy_scaler, HEPATITIS_C_SCALER_PATH)
                logger.warning("Created a dummy StandardScaler for Hepatitis C testing purposes.")
            hepatitis_c_scaler_instance = joblib.load(HEPATITIS_C_SCALER_PATH)
            logger.info(f"Loaded Hepatitis C Scaler from: {HEPATITIS_C_SCALER_PATH}")

        if hepatitis_c_feature_names_list is None:
            if not os.path.exists(HEPATITIS_C_FEATURE_NAMES_PATH):
                logger.warning(f"Hepatitis C Feature Names file not found: {HEPATITIS_C_FEATURE_NAMES_PATH}. Creating mock feature names.")
                # These are the 13 features expected by the dummy model and scaler
                dummy_feature_names = [
                    'Age', 'Sex', 'ALB', 'ALP', 'ALT', 'AST', 'BIL', 'CHE', 
                    'CHOL', 'CREA', 'GGT', 'PROT', 'AST_ALT'
                ]
                joblib.dump(dummy_feature_names, HEPATITIS_C_FEATURE_NAMES_PATH)
                logger.warning("Created dummy feature names list for Hepatitis C testing purposes.")
            hepatitis_c_feature_names_list = joblib.load(HEPATITIS_C_FEATURE_NAMES_PATH)
            logger.info(f"Loaded Hepatitis C Feature Names from: {HEPATITIS_C_FEATURE_NAMES_PATH}")

    except Exception as e:
        logger.critical(f"Failed to load Hepatitis C model artifacts: {e}", exc_info=True)
        # Clear instances to ensure subsequent calls also fail or retry appropriately
        hepatitis_c_model_instance = None
        hepatitis_c_scaler_instance = None
        hepatitis_c_feature_names_list = None
        raise

# Load artifacts on module import
try:
    load_hepatitis_c_artifacts()
except Exception as e:
    logger.error(f"Error during initial loading of Hepatitis C artifacts: {e}")

def preprocess_user_input_for_ml_hepatitis_c(user_input: Dict) -> pd.DataFrame:
    """
    Preprocesses raw user input data into a DataFrame suitable for Hepatitis C ML prediction.
    Ensures all expected features are present and in the correct order.
    Handles 'Sex' conversion (0 for Female, 1 for Male).
    Calculates 'AST_ALT' ratio if AST and ALT are available.
    """
    if hepatitis_c_feature_names_list is None:
        raise RuntimeError("Hepatitis C feature names not loaded. Cannot preprocess input.")

    # Create a mutable copy of the input data
    processed_input = user_input.copy()

    # Handle 'Sex'
    # Assuming Sex is provided as 0 or 1. If it's 'Male'/'Female', convert to 0/1.
    if 'Sex' in processed_input:
        if isinstance(processed_input['Sex'], str):
            processed_input['Sex'] = 1 if processed_input['Sex'].lower() == 'male' else 0
        # If it's already 0 or 1, no change needed.

    # Calculate AST_ALT ratio if AST and ALT are present
    if 'AST' in processed_input and 'ALT' in processed_input and processed_input['ALT'] != 0:
        processed_input['AST_ALT'] = processed_input['AST'] / processed_input['ALT']
    elif 'AST' in processed_input and 'ALT' in processed_input and processed_input['ALT'] == 0:
        processed_input['AST_ALT'] = processed_input['AST'] # Or handle as a specific high value, or NaN
        logger.warning("ALT is 0, AST_ALT ratio set to AST value or could be NaN. Review calculation for zero ALT.")
    else:
        processed_input['AST_ALT'] = 0.0 # Default if not present, though model might expect it

    # Create DataFrame with all expected features, filling missing with 0 or a sensible default
    # It's crucial that the order of columns matches the training data features.
    input_df = pd.DataFrame([processed_input])
    
    # Reindex to ensure all columns are present and in the correct order
    # Fill missing values with 0. This might need to be adjusted based on
    # how your ML model was trained to handle missing values.
    input_df = input_df.reindex(columns=hepatitis_c_feature_names_list, fill_value=0)
    
    logger.debug(f"Preprocessed ML input data (before scaling):\n{input_df}")
    return input_df

def _predict_hepatitis_c_ml_only(processed_data: pd.DataFrame) -> Dict:
    """
    Makes a prediction using the loaded Hepatitis C ML model.
    Assumes data is already preprocessed (scaled, correct features).
    """
    global hepatitis_c_model_instance
    global hepatitis_c_scaler_instance

    if hepatitis_c_model_instance is None or hepatitis_c_scaler_instance is None:
        logger.error("Hepatitis C model or scaler not loaded. Attempting to reload artifacts.")
        try:
            load_hepatitis_c_artifacts() # Try to reload
        except Exception as e:
            return {"error": "ML model or scaler not available", "details": str(e)}
        
        # After attempting reload, check again
        if hepatitis_c_model_instance is None or hepatitis_c_scaler_instance is None:
            return {"error": "ML model or scaler could not be loaded", "details": "Please check model artifact paths and dependencies."}

    try:
        # Scale the processed data
        scaled_data = hepatitis_c_scaler_instance.transform(processed_data)
        logger.debug(f"Scaled ML data shape: {scaled_data.shape}")

        # Make prediction
        predictions = hepatitis_c_model_instance.predict(scaled_data)
        logger.debug(f"Raw ML predictions: {predictions}")

        # Get probability of the positive class (assuming index 1 is positive, or max probability)
        # For a softmax output with multiple classes (e.g., 4 classes), you need to decide which
        # class probability represents "Hepatitis C". Often, class 1 might be "Hepatitis C (mild)",
        # class 2 "Hepatitis C (moderate)", class 3 "Hepatitis C (severe)".
        # For simplicity, let's assume `predictions[:, 1]` is the probability of *any* Hepatitis C,
        # or we take the max of disease-related classes if 0 is 'No Hep C'.
        
        # If class 0 is 'No Hepatitis C' and classes 1,2,3 are different stages of Hep C
        # we can sum probabilities of 1,2,3 or take the max of them.
        # Let's assume the highest probability among all classes (excluding the 'No Hepatitis C' class if it exists)
        # is the probability of "Hepatitis C" presence.
        
        # For demonstration, let's say class 0 is 'No Hepatitis C' and class 1 is 'Hepatitis C'.
        # If your model has multiple disease stages, you'd adapt this.
        if predictions.shape[1] > 1:
            # Assuming class 0 is 'No Hepatitis C' and any other class indicates presence.
            # We'll take 1 - probability of class 0 as the overall 'Hepatitis C detected' probability.
            probability_class_0 = predictions[0, 0] # Probability of 'No Hepatitis C'
            probability_class_1 = 1 - probability_class_0 # Probability of 'Hepatitis C' (any stage)
            prediction_class = 1 if probability_class_1 > 0.5 else 0 # Simple binary decision
        else: # Binary classifier (e.g., sigmoid output)
            probability_class_1 = predictions[0, 0]
            prediction_class = 1 if probability_class_1 > 0.5 else 0
        
        return {
            "prediction_class": prediction_class,
            "probability_class_1": float(probability_class_1), # Probability of "Hepatitis C"
            "probabilities_all_classes": predictions[0].tolist() # List of all class probabilities
        }
    except Exception as e:
        logger.error(f"Error during Hepatitis C ML prediction: {e}", exc_info=True)
        return {"error": "ML prediction failed", "details": str(e)}

# --- Main execution block for demonstration ---
if __name__ == "__main__":
    # Ensure artifacts are loaded before any prediction calls
    try:
        load_hepatitis_c_artifacts()
    except RuntimeError as e:
        print(f"Failed to load ML artifacts: {e}. ML predictions will not work.")

    # Example Usage:
    # Patient with high risk of Hepatitis C (due to critical lab values)
    patient_data_critical = {
        'Age': 65,
        'Sex': 1, # Male
        'ALB': 2.5,  # Critically low albumin
        'ALP': 300,  # High
        'ALT': 250,  # Very high
        'AST': 400,  # Very high
        'BIL': 4.5,  # High bilirubin
        'CHE': 2000, # Low
        'CHOL': 100, # Low
        'CREA': 2.0, # Elevated
        'GGT': 550,  # Very high
        'PROT': 5.5, # Low
        'AST_ALT': 1.6 # High ratio
    }

    # Patient with moderate risk
    patient_data_moderate = {
        'Age': 45,
        'Sex': 0, # Female
        'ALB': 3.8,
        'ALP': 130,
        'ALT': 70,
        'AST': 90,
        'BIL': 1.5,
        'CHE': 6000,
        'CHOL': 180,
        'CREA': 1.0,
        'GGT': 80,
        'PROT': 7.0,
        'AST_ALT': 1.2
    }

    # Patient with very low risk
    patient_data_low = {
        'Age': 30,
        'Sex': 0, # Female
        'ALB': 4.5,
        'ALP': 80,
        'ALT': 25,
        'AST': 20,
        'BIL': 0.5,
        'CHE': 8000,
        'CHOL': 160,
        'CREA': 0.8,
        'GGT': 30,
        'PROT': 7.5,
        'AST_ALT': 0.8
    }

    # Patient with missing essential data for rule-based system
    patient_data_missing_essential = {
        'Age': 50,
        'Sex': 1,
        'ALP': 150,
        'ALT': 80,
        'AST': 100,
        'BIL': 1.8,
        'GGT': 100,
        'PROT': 6.5,
        # 'ALB' and 'AST_ALT' are missing here
    }

    system = EnhancedHepatitisCDiagnosticSystem()

    print("\n--- Critical Patient Diagnosis ---")
    result_critical = system.predict_with_hybrid_approach(patient_data_critical)
    import json
    print(json.dumps(result_critical, indent=2))

    print("\n--- Moderate Patient Diagnosis ---")
    result_moderate = system.predict_with_hybrid_approach(patient_data_moderate)
    print(json.dumps(result_moderate, indent=2))

    print("\n--- Low Risk Patient Diagnosis ---")
    result_low = system.predict_with_hybrid_approach(patient_data_low)
    print(json.dumps(result_low, indent=2))

    print("\n--- Patient with Missing Essential Rule Data ---")
    result_missing = system.predict_with_hybrid_approach(patient_data_missing_essential)
    print(json.dumps(result_missing, indent=2))

    # Clean up dummy artifacts in a temporary directory
    if MODELS_BASE_DIR.startswith(tempfile.gettempdir()):
        try:
            import shutil
            shutil.rmtree(HEPATITIS_C_MODEL_DIR) # Changed to HEPATITIS_C_MODEL_DIR
            print(f"\nCleaned up dummy model directory: {MODELS_BASE_DIR}")
        except OSError as e:
            print(f"Error removing dummy model directory {MODELS_BASE_DIR}: {e}")

def preprocess_user_input_for_ml_hepatitis_c(user_input: Dict) -> Dict:
    """
    Converts user-friendly input for Hepatitis C into the ML-ready numerical format.
    Ensures that the output dictionary contains all features expected by the ML model.
    """
    processed_data = {}
    logger.debug("--- Preprocessing Hepatitis C User Input for ML ---")

    # Handle numerical features, with sensible defaults if missing
    # Ensure values are floats
    processed_data['Age'] = float(user_input.get('Age', 45.0))
    processed_data['ALB'] = float(user_input.get('ALB', 4.0))
    processed_data['ALP'] = float(user_input.get('ALP', 80.0))
    processed_data['ALT'] = float(user_input.get('ALT', 30.0))
    processed_data['AST'] = float(user_input.get('AST', 30.0))
    processed_data['BIL'] = float(user_input.get('BIL', 0.8))
    processed_data['CHE'] = float(user_input.get('CHE', 8000.0))
    processed_data['CHOL'] = float(user_input.get('CHOL', 180.0))
    processed_data['CREA'] = float(user_input.get('CREA', 0.9))
    processed_data['GGT'] = float(user_input.get('GGT', 25.0))
    processed_data['PROT'] = float(user_input.get('PROT', 7.0))

    # Calculate AST/ALT ratio, handle division by zero
    ast = processed_data.get('AST', 0.0)
    alt = processed_data.get('ALT', 0.0)
    processed_data['AST_ALT'] = ast / alt if alt != 0 else 0.0
    logger.debug(f"  Calculated AST_ALT: {processed_data['AST_ALT']:.2f} (from AST={ast}, ALT={alt})")

    # Sex: 'Male' -> 1, 'Female' -> 0 (Assuming your ML model expects 0 for Female, 1 for Male)
    sex_input = str(user_input.get('Sex', '')).lower()
    processed_data['Sex'] = 1 if sex_input == 'male' else 0 # Assuming 'f' -> female -> 0
    logger.debug(f"  Preprocessing Sex: '{user_input.get('Sex')}' -> Sex={processed_data['Sex']}")

    # Handle AgeGroup features if your ML model was trained with them as separate columns.
    # If your actual ML model was trained with 'AgeGroup_Middle' and 'AgeGroup_Old' as direct features,
    # uncomment the following lines and ensure they are also in your `hepatitis_c_feature_names_list`.
    # age = processed_data['Age']
    # processed_data['AgeGroup_Middle'] = 1 if (age >= 30 and age < 60) else 0
    # processed_data['AgeGroup_Old'] = 1 if age >= 60 else 0
    # logger.debug(f"  AgeGroup_Middle: {processed_data['AgeGroup_Middle']}, AgeGroup_Old: {processed_data['AgeGroup_Old']}")

    logger.debug(f"Final processed data for ML: {processed_data}")
    return processed_data

# Instantiate the diagnostic system (for direct use or Flask endpoint)
hepatitis_c_diagnostic_system = EnhancedHepatitisCDiagnosticSystem()

# Example usage (for testing purposes)
if __name__ == "__main__":
    # Ensure dummy models are created if they don't exist
    load_hepatitis_c_artifacts() 

    # Test cases
    test_cases = [
        {
            "description": "Critical Case 1: High AST/ALT and low ALB (simulating advanced fibrosis)",
            "data": {
                "Age": 60, "Sex": "f", "ALB": 2.8, "ALP": 150, "ALT": 50, "AST": 100, 
                "BIL": 2.5, "CHE": 3000, "CHOL": 100, "CREA": 1.5, "GGT": 300, "PROT": 5.0, "AST_ALT": 2.0
            }
        },
        {
            "description": "Critical Case 2: Severely elevated ALT/AST and high BIL",
            "data": {
                "Age": 55, "Sex": "m", "ALB": 3.5, "ALP": 180, "ALT": 250, "AST": 300, 
                "BIL": 4.5, "CHE": 6000, "CHOL": 170, "CREA": 1.0, "GGT": 80, "PROT": 7.0, "AST_ALT": 1.2
            }
        },
        {
            "description": "High Risk Case: Multiple abnormal markers",
            "data": {
                "Age": 45, "Sex": "f", "ALB": 3.2, "ALP": 130, "ALT": 70, "AST": 90, 
                "BIL": 1.5, "CHE": 7000, "CHOL": 220, "CREA": 0.8, "GGT": 60, "PROT": 6.5, "AST_ALT": 1.28
            }
        },
        {
            "description": "Moderate Risk Case: Elevated ALT/AST only",
            "data": {
                "Age": 35, "Sex": "m", "ALB": 4.0, "ALP": 100, "ALT": 65, "AST": 55, 
                "BIL": 0.9, "CHE": 9000, "CHOL": 190, "CREA": 0.9, "GGT": 40, "PROT": 7.5, "AST_ALT": 0.85
            }
        },
        {
            "description": "Low Risk Case: All values normal or near normal",
            "data": {
                "Age": 28, "Sex": "f", "ALB": 4.5, "ALP": 70, "ALT": 25, "AST": 20, 
                "BIL": 0.5, "CHE": 10000, "CHOL": 160, "CREA": 0.8, "GGT": 20, "PROT": 7.2, "AST_ALT": 0.8
            }
        }
    ]

    for case in test_cases:
        print("\n" + "="*50)
        print(f"TEST CASE: {case['description']}")
        print("="*50)
        
        result = hepatitis_c_diagnostic_system.predict_with_hybrid_approach(case['data'])
        
        print("\n--- Diagnosis Result ---")
        print(f"Diagnosis: {result.get('diagnosis')}")
        print(f"Probability: {result.get('probability'):.2f}")
        print(f"Risk Level: {result.get('risk_level')}")
        print(f"Decision Method: {result.get('decision_method')}")