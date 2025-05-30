import logging
from flask import request, jsonify
import numpy as np

def predict_malaria(models, process_image):
    if models["malaria"] is None:
        return jsonify({"error": "Malaria model not loaded"}), 500

    if 'file' not in request.files or request.files['file'].filename == '':
        return jsonify({"error": "No valid image file uploaded"}), 400

    try:
        image_data = request.files['file'].read()
        processed_image = process_image(image_data)
        prediction = np.argmax(models["malaria"].predict(processed_image), axis=1)[0]
        diagnosis_message = "Parasitized. Please consult a doctor for further evaluation." if prediction == 1 else "Uninfected."
        return jsonify({"diagnosis": int(prediction), "message": diagnosis_message})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logging.error(f"Error processing Malaria request: {e}")
        return jsonify({"error": "Error processing image or prediction"}), 500