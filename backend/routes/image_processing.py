from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import tensorflow as tf
import numpy as np
from PIL import Image, UnidentifiedImageError
import io
import logging
import os


# Configure logging for this blueprint
# Note: If main app (app.py) also configures logging, this might be redundant
# or could override. It's best to configure once in app.py or a shared config.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Define Blueprint
image_bp = Blueprint("image_processing", __name__)


# Dynamically determine the model path for Render compatibility
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Adjust based on blueprint location
MODEL_PATH = os.path.join(BASE_DIR, "models", "multi_class_malaria_model", "multi_class_malaria_model.h5")


# Load the model safely
model = None
try:
    if os.path.exists(MODEL_PATH):
        model = tf.keras.models.load_model(MODEL_PATH)
        logging.info(f"Model loaded successfully from: {MODEL_PATH}")
    else:
        logging.error(f"Model file not found at: {MODEL_PATH}")
except Exception as e:
    logging.error(f"Failed to load model from {MODEL_PATH}: {e}")


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
            logging.error("Model is not loaded. Returning 500.")
            return jsonify({"error": "Model not loaded. Check server logs for details."}), 500

        # *** IMPORTANT FIX: Check for "file" instead of "image" based on our previous discussion
        # If your frontend is configured to send with "image", change this back to "image"
        # However, "file" is a common and often preferred key for file uploads in Flask.
        if "file" not in request.files: # Changed from "image"
            logging.warning("No 'file' key in request.files. Returning 400.")
            return jsonify({"error": "No image file found with key 'file'. Please ensure your form data key matches."}), 400

        image_file = request.files["file"] # Changed from "image"
        
        if image_file.filename == '':
            logging.warning("Empty filename received. Returning 400.")
            return jsonify({"error": "No selected image file."}), 400

        filename = secure_filename(image_file.filename) # Secure filename for good practice


        try:
            # Read the image data once
            image_bytes = image_file.read()
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            img = img.resize((128, 128))
            img_array = np.array(img) / 255.0  # Normalize
            img_array = img_array.reshape(1, 128, 128, 3)  # Reshape for model input
        except UnidentifiedImageError:
            logging.error(f"Invalid image format for file {filename}. Returning 400.")
            return jsonify({"error": "Invalid image format. Please use JPEG or PNG."}), 400
        except Exception as img_proc_e:
            logging.error(f"Error during image preprocessing for {filename}: {img_proc_e}. Returning 400.")
            return jsonify({"error": f"Error processing image: {str(img_proc_e)}"}), 400


        prediction = model.predict(img_array)
        predicted_class_index = np.argmax(prediction)
        
        # IMPORTANT: Ensure this order matches the output classes of your model.
        class_labels = ['Parasitized', 'Uninfected', 'NonBloodSmear']
        
        predicted_class = class_labels[predicted_class_index]
        confidence = float(prediction[0][predicted_class_index])


        threshold = 0.7  # Example confidence threshold


        # Determine the final diagnosis message and whether to show probability
        diagnosis_message = ""
        is_non_smear = False # Flag for frontend
        
        if predicted_class == "NonBloodSmear":
            diagnosis_message = prescriptions.get("Non-Blood Smear") # Use prescription text
            is_non_smear = True
            # For non-blood smear, frontend might choose not to show probability
            # We can still send it, but frontend should handle `isNonSmear` flag.
        elif predicted_class == "Parasitized":
            if confidence < threshold:
                diagnosis_message = prescriptions.get("Uncertain")
            else:
                diagnosis_message = prescriptions.get("Malaria Detected")
        elif predicted_class == "Uninfected":
            if confidence < threshold:
                diagnosis_message = prescriptions.get("Uncertain")
            else:
                diagnosis_message = prescriptions.get("No Malaria Detected")
        else: # Fallback for any unexpected prediction index
            diagnosis_message = "Unknown diagnosis. Please ensure the model and class labels are correctly configured."
            
        logging.info(f"Prediction: {diagnosis_message}, Probability: {confidence:.4f}, Predicted Class: {predicted_class}")


        # Return response in a format that your React frontend expects from previous discussions
        return jsonify({
            "diagnosis_message": diagnosis_message,
            "probability": round(confidence, 4), # Round for cleaner output
            "predicted_class_label": predicted_class, # Send the raw predicted class label
            "isNonSmear": is_non_smear # Explicitly tell frontend if it's non-smear
        })


    except Exception as e:
        logging.exception(f"An unexpected error occurred during request processing: {e}")
        return jsonify({"error": f"An internal server error occurred: {str(e)}"}), 500

