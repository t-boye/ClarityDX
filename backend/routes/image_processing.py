from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import tensorflow as tf
import numpy as np
from PIL import Image, UnidentifiedImageError
import io
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define Blueprint
image_bp = Blueprint("image_processing", __name__)

# Load trained model
model = tf.keras.models.load_model(r"C:\Users\USER\Documents\GitHub\malaria-expert-system\backend\models\multi_class_malaria_model\multi_class_malaria_model.h5")

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

        # Adjusted Logic: Corrected prediction logic and non-blood smear handling
        threshold = 0.7  # Example confidence threshold. Adjust as needed.

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
            result = "Uncertain" # fallback case

        logging.info(f"Prediction: {result}, Probability: {confidence}, Predicted Class: {predicted_class}")

        # Get the prescription based on the result
        prescription = prescriptions.get(result, "Prescription information not available.")

        return jsonify({"diagnosis": result, "probability": confidence, "prescription": prescription, "predicted_class" : predicted_class})

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500