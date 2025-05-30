import logging
from flask import request, jsonify
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, ValidationError
from typing import Dict, List, Union

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


def predict_heart_disease(models, feature_names):
    """
    Predicts heart disease and provides a detailed diagnostic interpretation.
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

        # Create detailed interpretation
        interpretation = get_heart_disease_interpretation(input_data, prediction, feature_names)

        # Enhanced Response Formatting
        response_data: Dict[str, Union[float, str, Dict[str, Union[str, float]]]] = {
            "prediction": float(prediction),
            "diagnosis": interpretation["diagnosis"],
            "severity": interpretation["severity"],
            "interpretation": interpretation
        }

        return jsonify(response_data), 200

    except Exception as e:
        logging.error(f"Heart Disease - Error processing request: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


def get_heart_disease_interpretation(input_data: pd.DataFrame, prediction: float, feature_names: List[str]) -> Dict[str, Union[str, Dict[str, float]]]:
    """
    Provides a detailed interpretation of the heart disease prediction.

    Args:
        input_data (pd.DataFrame): The input data used for prediction.
        prediction (float): The predicted probability of heart disease.
        feature_names (List[str]): List of feature names corresponding to input_data.

    Returns:
        Dict[str, Union[str, Dict[str, float]]]: A dictionary containing the diagnosis, severity,
                                              and detailed interpretation of risk factors.
    """

    interpretation: Dict[str, Union[str, Dict[str, float]]] = {}

    # Enhanced Diagnostic Messaging
    if prediction > 0.5:
        interpretation["diagnosis"] = (
            "Likelihood of Heart Disease Detected. It is strongly recommended to consult a doctor for further evaluation and testing."
        )
        interpretation["severity"] = "High"
    elif prediction > 0.2:  # Adjust this threshold as needed
        interpretation["diagnosis"] = (
            "Possible indication of Heart Disease. Further investigation may be warranted. Please consult with a healthcare professional."
        )
        interpretation["severity"] = "Moderate"
    else:
        interpretation["diagnosis"] = "Low likelihood of Heart Disease detected. However, if you are experiencing symptoms, it is advisable to seek medical advice."
        interpretation["severity"] = "Low"

    # Analyze risk factors (THIS IS A PLACEHOLDER - NEEDS MEDICAL EXPERTISE)
    risk_factors: Dict[str, float] = {}
    for i, feature in enumerate(feature_names):
        value = input_data[feature].values[0]

        if feature == "age" and value > 60:
            risk_factors["Age"] = value
        if feature == "chol" and value > 240: # Example threshold
            risk_factors["Cholesterol"] = value
        if feature == "thalach" and value < 100: # Example threshold
            risk_factors["Max Heart Rate"] = value

    if risk_factors:
        interpretation["significant_risk_factors"] = {
            "message": "Significant risk factors identified:",
            "factors": risk_factors
        }
    else:
        interpretation["significant_risk_factors"] = {"message": "No significant risk factors identified based on the model's criteria."}

    interpretation["disclaimer"] = "This is a prediction, not a diagnosis. Consult a medical professional for accurate diagnosis and treatment."

    return interpretation