import logging
from flask import request, jsonify
import numpy as np
from pydantic import BaseModel, Field, ValidationError
import json  # Import the json module
from tensorflow import keras
import pandas as pd
import joblib
from typing import List, Dict, Union, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)

# Feature names, MUST match the order used to train the model.  Define it here, at the top level
hepatitis_c_model_feature_names = ['Age', 'Sex', 'ALB', 'ALP', 'ALT', 'AST', 'BIL', 'CHE', 'CHOL', 'CREA', 'GGT', 'PROT', 'AST/ALT', 'AgeGroup_Middle', 'AgeGroup_Old']


# Revert HepatitisCData model to include all 15 features
class HepatitisCData(BaseModel):
    Age: float = Field(..., alias="Age")
    Sex: str = Field(..., alias="Sex")  # Changed to str to handle "m" or "f"
    ALB: float = Field(..., alias="ALB")
    ALP: float = Field(..., alias="ALP")
    ALT: float = Field(..., alias="ALT")
    AST: float = Field(..., alias="AST")
    BIL: float = Field(..., alias="BIL")
    CHE: float = Field(..., alias="CHE")
    CHOL: float = Field(..., alias="CHOL")
    CREA: float = Field(..., alias="CREA")
    GGT: float = Field(..., alias="GGT")
    PROT: float = Field(..., alias="PROT")
    AST_ALT: float = Field(..., alias="AST/ALT")  # Added AST/ALT
    AgeGroup_Middle: int = Field(..., alias="AgeGroup_Middle")  # Added AgeGroup_Middle
    AgeGroup_Old: int = Field(..., alias="AgeGroup_Old")  # Added AgeGroup_Old


# Function to load the scaler
def load_scaler(scaler_path='scaler.pkl'):
    """
    Loads the RobustScaler from a file.

    Args:
        scaler_path (str, optional): Path to the scaler file. Defaults to 'scaler.pkl'.

    Returns:
        RobustScaler: The loaded scaler, or None if loading fails.
    """
    try:
        scaler = joblib.load(scaler_path)
        logging.info("Scaler loaded successfully from %s", scaler_path)
        return scaler
    except Exception as e:
        logging.error("Error loading scaler from %s: %s", scaler_path, e)
        return None


# Function to predict Hepatitis C
def predict_hepatitis_c(models, hepatitis_c_model_feature_names, scaler=None):  # Add scaler as argument
    """
    Predicts Hepatitis C status based on input data.

    Args:
        models (dict): A dictionary containing the loaded machine learning models.
        hepatitis_c_model_feature_names (list): List of feature names expected by the Hepatitis C model.
        scaler (RobustScaler, optional):  The scaler to use for data transformation.

    Returns:
        jsonify: A JSON response containing the prediction and associated information.
    """
    if models["hepatitis_c"] is None:
        return jsonify({"error": "Hepatitis C model not loaded"}), 500

    try:
        raw_json = request.get_json(force=True)
        logging.info(f"Received JSON: {json.dumps(raw_json, indent=4)}")

        # Validate the input data using the Pydantic model
        try:
            data = HepatitisCData.model_validate(raw_json)
        except ValidationError as e:
            logging.error(f"Pydantic validation error: {e}")
            return jsonify({"error": f"Invalid input data: {e}"}), 400
        logging.info(f"Hepatitis C input data: {data.model_dump()}")

        # Handle the 'Sex' field, raising an error for invalid values
        sex_mapping = {'m': 0, 'f': 1}
        sex = sex_mapping.get(data.Sex)
        if sex is None:
            error_msg = f"Invalid sex value: {data.Sex}. Must be 'm' or 'f'"
            logging.error(error_msg)
            return jsonify({"error": error_msg}), 400
        logging.info(f"Processed sex value: {sex}")

        # Create input array for the model, ensuring correct order and shape
        input_data = np.array([
            data.Age,
            sex,
            data.ALB,
            data.ALP,
            data.ALT,
            data.AST,
            data.BIL,
            data.CHE,
            data.CHOL,
            data.CREA,
            data.GGT,
            data.PROT,
            data.AST_ALT,
            data.AgeGroup_Middle,
            data.AgeGroup_Old
        ]).reshape(1, -1)  # Reshape to (1, 15)
        logging.info(f"Input data before scaling: {input_data}")
        logging.info(f"Input data shape: {input_data.shape}")

        # Impute missing values using the median.  Uses pandas
        input_df = pd.DataFrame(input_data, columns=hepatitis_c_model_feature_names)
        for col in ['ALB', 'ALP', 'ALT', 'CHOL', 'PROT']:
            if input_df[col].isnull().any():  # Check for nulls *before* imputation
                median_val = input_df[col].median()
                input_df[col] = input_df[col].fillna(median_val)
                logging.warning(f"Missing value in {col}, imputed with median {median_val}")
        input_data = input_df.values  # convert back to numpy array
        logging.info(f"Input data shape after imputation: {input_data.shape}")

        # Scale the input data, handling the case where the scaler is None
        if scaler is not None:
            input_data_scaled = scaler.transform(input_data)
            logging.info(f"Scaled input data: {input_data_scaled}")
            logging.info(f"Scaled input data shape: {input_data_scaled.shape}")
        else:
            input_data_scaled = input_data
            logging.warning("Scaler not loaded; proceeding with unscaled data. This may affect prediction accuracy.")

        # Get multi-class prediction (TensorFlow model)
        try:
            prediction_probs = models["hepatitis_c"].predict(input_data_scaled)
            logging.info(f"Shape of data going into model: {input_data_scaled.shape}")
            logging.info(f"Shape of model output: {prediction_probs.shape}")
            predicted_class = np.argmax(prediction_probs, axis=-1)[0]
            logging.info(f"Hepatitis C prediction probabilities: {prediction_probs}")
            logging.info(f"Hepatitis C predicted class: {predicted_class}")

            # Detailed response including probabilities and interpretation
            response_data = create_diagnosis_response(input_data, prediction_probs, hepatitis_c_model_feature_names, predicted_class)

            return jsonify(response_data)

        except ValueError as e:
            logging.error(f"Model prediction error: {e}, with input shape {input_data_scaled.shape}")
            return jsonify({"error": f"Error during prediction: {e}"}), 500

    except ValueError as ve:
        logging.error(f"Invalid input data for Hepatitis C: {ve}")
        return jsonify({"error": f"Invalid input data: {ve}"}), 400
    except KeyError as ke:
        logging.error(f"Key error during Hepatitis C processing: {ke}")
        return jsonify({"error": f"Key error: {ke}"}), 400
    except Exception as e:
        logging.error(f"Error processing Hepatitis C request: {e}", exc_info=True)
        return jsonify({"error": "An internal error occurred"}), 500


def create_diagnosis_response(input_data: np.ndarray, probabilities: np.ndarray, feature_names: List[str], predicted_class: int) -> Dict[str, Union[int, str, List[float], Dict[str, Union[float, str]]]]:
    """
    Creates a comprehensive diagnosis response including prediction, probabilities,
    and interpretation of risk factors.

    Args:
        input_data (np.ndarray): The input data used for prediction.
        probabilities (np.ndarray): List of probabilities for each Hepatitis C category.
        feature_names (List[str]): List of feature names corresponding to input_data.
        predicted_class (int): The predicted Hepatitis C category.

    Returns:
        Dict[str, Union[int, str, List[float], Dict[str, Union[float, str]]]]:
            A dictionary containing the diagnosis response.
    """

    diagnosis_messages = {
        0: "No Hepatitis C Detected. ✅ Likely healthy.",
        1: "Hepatitis C Detected. ❗️ High probability. Further evaluation by a specialist is crucial.",
        2: "Hepatitis C Detected. ⚠️ Moderate probability. Additional tests (e.g., PCR) are recommended.",
        3: "Hepatitis C Detected. 🚨 Significant probability. Urgent specialist consultation is advised.",
        4: "Hepatitis C Detected. 🆘 Critical probability. Immediate medical intervention is necessary."
    }
    diagnosis_message: str = diagnosis_messages.get(predicted_class, "Unknown Hepatitis C Category.")

    interpretation: Dict[str, Union[float, str]] = get_detailed_interpretation(input_data, probabilities, feature_names)

    # --- ENSURE predicted_class IS A PYTHON INT ---
    response_data: Dict[str, Union[int, str, List[float], Dict[str, Union[float, str]]]] = {
        "predicted_class": int(predicted_class),  # Explicitly convert to Python int
        "diagnosis": diagnosis_message,
        "probabilities": probabilities.tolist(),
        "interpretation": interpretation
    }
    # --- END ENSURE predicted_class IS A PYTHON INT ---

    return response_data


def get_detailed_interpretation(input_data: np.ndarray, probabilities: np.ndarray, feature_names: List[str]) -> Dict[str, Union[str, List[Dict[str, Union[float, str]]]]]:
    """
    Provides a detailed interpretation of the prediction probabilities,
    considering individual risk factors.

    Args:
        input_data (np.ndarray): The input data used for prediction.
        probabilities (np.ndarray): List of probabilities for each Hepatitis C category.
        feature_names (List[str]): List of feature names corresponding to input_data.

    Returns:
        Dict[str, Union[str, List[Dict[str, Union[float, str]]]]]:
            A dictionary containing a detailed interpretation.
    """

    interpretation: Dict[str, Union[str, List[Dict[str, Union[float, str]]]]] = {}
    probabilities_list: List[List[float]] = probabilities.tolist()

    for i, prob_list in enumerate(probabilities_list):
        interpretation[f"Category {i}"] = []
        for j, prob in enumerate(prob_list):
            interpretation[f"Category {i}"].append({"probability": float(prob), "reason": f"Probability of Category {i}"})


    # Analyze individual risk factors (This is a placeholder and needs medical expertise)
    risk_factors: List[str] = []
    input_dict: Dict[str, float] = dict(zip(feature_names, input_data[0]))  # Create dict for easier access

    if input_dict['Age'] > 55:  # Example: Age > 55 is significant
        risk_factors.append("Advanced age (increased risk of complications)")
    if input_dict['ALT'] > 2 * 40:  # Example: ALT > 2x upper limit of normal (ULN)
        risk_factors.append("Significantly elevated ALT (liver inflammation)")
    if input_dict['AST'] > 2 * 40:  # Example: AST > 2x ULN
        risk_factors.append("Significantly elevated AST (liver damage)")
    if input_dict['BIL'] > 2.0:  # Example: Bilirubin above a certain threshold
        risk_factors.append("Elevated bilirubin (potential liver dysfunction)")

    if risk_factors:
        interpretation["significant_risk_factors"] = f"Significant risk factors identified: {', '.join(risk_factors)}."
    else:
        interpretation["significant_risk_factors"] = "No significant risk factors identified based on the model's criteria."

    interpretation["disclaimer"] = "This is a prediction, not a diagnosis. Consult a medical professional for accurate diagnosis and treatment."
    return interpretation


if __name__ == '__main__':
    # Load models (replace with your actual model loading logic)
    models = {
        "hepatitis_c": keras.models.load_model('hepatitis_c_model.keras') if keras else None,  # Example
        # Add other models as needed
    }
    # Load the scaler
    scaler = load_scaler()  # Load the scaler
    if scaler is None:
        print("Failed to load the scaler. The application will proceed without scaling.")
    # Example usage (replace with your actual Flask app setup)
    # from flask import Flask
    # app = Flask(__name__)

    # @app.route('/predict_hepatitis_c', methods=['POST'])
    # def predict_route():
    #     return predict_hepatitis_c(models, hepatitis_c_model_feature_names, scaler)

    # if __name__ == '__main__':
    #     app.run(debug=True)