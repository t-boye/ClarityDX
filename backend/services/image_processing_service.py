import tensorflow as tf
import numpy as np
from PIL import Image
import io

# Load trained model (updated from .pkl to .h5)
model = tf.keras.models.load_model(r"C:\Users\USER\Documents\GitHub\malaria-expert-system\backend\models\multi_class_malaria_model\multi_class_malaria_model.h5")

def process_image(image):
    try:
        img = Image.open(io.BytesIO(image.read())).convert("RGB")
        img = img.resize((128, 128))
        img_array = np.array(img) / 255.0  # Normalize
        img_array = img_array.reshape(1, 128, 128, 3)  # Reshape for model input

        prediction = model.predict(img_array)
        return "Malaria Detected" if prediction[0][0] > 0.5 else "No Malaria Detected"
    except Exception as e:
        return f"Error processing image: {str(e)}"
