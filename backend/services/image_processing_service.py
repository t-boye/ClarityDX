import os
import tensorflow as tf
import numpy as np
from PIL import Image
import io

# Automatically get the absolute path to the model, relative to this file
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "multi_class_malaria_model", "multi_class_malaria_model.h5")

# Load the model once when the service starts
try:
    model = tf.keras.models.load_model(MODEL_PATH)
except Exception as e:
    model = None
    print(f"[ERROR] Could not load model from {MODEL_PATH}: {e}")

def process_image(image):
    if model is None:
        return "Model not loaded. Please check server logs."

    try:
        img = Image.open(io.BytesIO(image.read())).convert("RGB")
        img = img.resize((128, 128))
        img_array = np.array(img) / 255.0  # Normalize
        img_array = img_array.reshape(1, 128, 128, 3)  # Reshape for model input

        prediction = model.predict(img_array)

        # Example assumes binary classification. Adjust for multi-class if needed.
        return "Malaria Detected" if prediction[0][0] > 0.5 else "No Malaria Detected"

    except Exception as e:
        return f"Error processing image: {str(e)}"
