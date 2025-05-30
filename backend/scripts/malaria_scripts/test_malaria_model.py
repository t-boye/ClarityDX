import numpy as np
from PIL import Image, UnidentifiedImageError
import os
import tensorflow as tf
from tensorflow.keras.models import load_model

# Ensure the 'models' folder exists
model_path = r"C:\Users\USER\Documents\GitHub\malaria-expert-system\backend\models\multi_class_malaria_model\multi_class_malaria_model.h5"

# Load the trained model with error handling
if not os.path.exists(model_path):
    raise FileNotFoundError(f"❌ Model file not found: {model_path}. Ensure the model is saved properly.")

# Load the model using TensorFlow/Keras
model = load_model(model_path)
print("✅ Model loaded successfully!")

# Function to preprocess images (using PIL)
def preprocess_image(image_path):
    """Load and preprocess the image for model prediction using PIL."""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"❌ Test image not found: {image_path}. Place a test image in the correct folder.")

    try:
        img = Image.open(image_path).convert("RGB")  # Open and convert to RGB
        img = img.resize((128, 128))  # Resize to match training size
        img_array = np.array(img) / 255.0  # Normalize pixel values (0 to 1)
        img_array = img_array.reshape(1, 128, 128, 3)  # Reshape for model input
        return img_array

    except UnidentifiedImageError:
        raise ValueError(f"❌ Could not read image: {image_path}. Ensure it's a valid image file.")

# Define test image path
test_image_path = r"C:\Users\USER\Documents\GitHub\malaria-expert-system\backend\dataset\malaria\test\Uninfected\C1_thinF_IMG_20150604_104722_cell_15.png"

# Process and test the image
try:
    image = preprocess_image(test_image_path)
    prediction = model.predict(image)
    probability = float(prediction[0][0])  # Get the probability

    # Corrected logic: 0 means no malaria, 1 means malaria
    predicted_label = "Malaria Detected" if probability > 0.5 else "No Malaria Detected"

    print(f"🩺 Prediction: {predicted_label}, Probability: {probability}")

    # Flag images that are incorrect or outside of the two main classes.
    if "NonBloodSmear" in test_image_path:
        print(f"🚩 Non-smear image detected: {test_image_path}")
    elif ("Malaria Detected" in predicted_label and "Uninfected" in test_image_path) or ("No Malaria Detected" in predicted_label and "Parasitized" in test_image_path):
        print(f"🚩 Incorrect prediction for malaria classification: {test_image_path}")

except Exception as e:
    print(f"❌ An error occurred during testing: {e}")
    print(f"❌ Error: {e}")