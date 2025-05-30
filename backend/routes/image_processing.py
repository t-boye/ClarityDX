from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import tensorflow as tf
import numpy as np
from PIL import Image, UnidentifiedImageError
import io
import logging
import os  # ✅ Added for path handling

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define Blueprint
image_bp = Blueprint("image_processing", __name__)

# ✅ Dynamically determine the model path for Render compatibility
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "multi_class_malaria_model", "multi_class_malaria_model.h5")

# ✅ Load the model safely
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    logging.info(f"Model loaded from: {MODEL_PATH}")
except Exception as e:
    logging.error(f"Failed to load model from {MODEL_PATH}: {e}")
    model = None

# Prescription data
prescriptions = {
    "Malaria Detected": "Artemether-lumefantrine (Coartem) is recommended. Take one tablet twice daily for three days. Consult a healthcare professional for dosage and duration.",
    "No Malaria Detected": "No antimalarial medication is required. If symptoms persist, consult a healthcare professional.",
    "Non-Blood Smear": "This image is not a blood smear. Please upload a blood smear image.",
    "Uncertain": "The image could not be reliably classified. Please upload a clearer blood smear image."
}

@image_bp.route("/process-image", methods=["POST"])
def process_image():
    logging.info("Request received to process image")
    try:
        if model is None:
            return jsonify({"error": "Model not loaded. Check logs for details."}), 500

        if "image" not in request.files:
            return jsonify({"error": "No image file found"}), 400

        image_file = request.files["image"]
        filename = secure_filename(image_file.filename)

        try:
            img = Image.open(io.BytesIO(image_file.read())).convert("RGB")
            img = img.resize((128, 128))
            img_array = np.array(img) / 255.0  # Normalize
            img_array = img_array.reshape(1, 128, 128, 3)  # Reshape for model input
        except UnidentifiedImageError:
            return jsonify({"error": "Invalid image format. Please use JPEG or PNG."}), 400

        prediction = model.predict(img_array)
        predicted_class_index = np.argmax(prediction)
        class_labels = ['Parasitized', 'Uninfected', 'NonBloodSmear']
        predicted_class = class_labels[predicted_class_index]
        confidence = float(prediction[0][predicted_class_index])

        threshold = 0.7  # Example confidence threshold

        if predicted_class == "NonBloodSmear" or confidence < threshold:
            if predicted_class == "NonBloodSmear":
                result = "Non-Blood Smear"
            else:
                result = "Uncertain"
        elif predicted_class == "Parasitized":
            result = "Malaria Detected"
        elif predicted_class == "Uninfected":
            result = "No Malaria Detected"
        else:
            result = "Uncertain"

        logging.info(f"Prediction: {result}, Probability: {confidence}, Predicted Class: {predicted_class}")

        prescription = prescriptions.get(result, "Prescription information not available.")

        return jsonify({
            "diagnosis": result,
            "probability": confidence,
            "prescription": prescription,
            "predicted_class": predicted_class
        })

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500
