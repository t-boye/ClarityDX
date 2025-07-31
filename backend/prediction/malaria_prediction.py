import logging
from flask import request, jsonify
import numpy as np

def predict_malaria(models, process_image):
    """
    Predicts malaria presence from an uploaded image, handles multi-class outputs
    including 'NonBloodSmear', and conditionally includes prediction probability.

    Args:
        models (dict): A dictionary containing loaded machine learning models,
                       e.g., {"malaria": tf.keras.Model_object}.
        process_image (function): A function that takes raw image data (bytes)
                                  and returns a preprocessed numpy array ready
                                  for model prediction.

    Returns:
        tuple: A Flask jsonify response and HTTP status code.
    """
    if models["malaria"] is None:
        logging.error("Malaria model is not loaded. Cannot process request.")
        return jsonify({"error": "Malaria model not loaded. Please check server configuration."}), 500

    # *** IMPORTANT CHANGE HERE: Check for 'image' instead of 'file' ***
    if 'image' not in request.files or request.files['image'].filename == '':
        logging.warning("No valid image file uploaded in the request (expected key 'image').")
        # Changed error message to reflect the expected key
        return jsonify({"error": "No valid image file uploaded. Please ensure the 'image' field is present."}), 400

    try:
        # *** IMPORTANT CHANGE HERE: Access 'image' from request.files ***
        image_file = request.files['image']
        image_data = image_file.read()

        # Call the external process_image function to prepare the image for the model
        processed_image = process_image(image_data)
        
        # Get raw predictions (probabilities for each class)
        # The model is expected to output probabilities for ['Uninfected', 'Parasitized', 'NonBloodSmear']
        raw_predictions = models["malaria"].predict(processed_image)
        
        # Get the index of the class with the highest probability
        predicted_class_index = np.argmax(raw_predictions, axis=1)[0]
        
        # Get the confidence for the predicted class
        confidence = float(raw_predictions[0][predicted_class_index])

        # Define your class labels based on how your multi_class_malaria_model was trained.
        # IMPORTANT: Ensure this order matches the output classes of your model.
        class_labels = ['Uninfected', 'Parasitized', 'NonBloodSmear'] # Example order

        diagnosis_message = ""
        # Default probability to show is the confidence, will be set to None for NonBloodSmear
        probability_to_show = confidence 

        # Define a confidence threshold for 'blood smear' classes to be considered 'Uncertain'
        blood_smear_confidence_threshold = 0.7 # This threshold can be tuned

        # Determine the final diagnosis message and whether to show probability
        if class_labels[predicted_class_index] == "NonBloodSmear":
            diagnosis_message = "This image is not a blood smear. Please upload a blood smear image."
            probability_to_show = None  # Do not show probability for non-blood smear
        elif class_labels[predicted_class_index] == "Parasitized":
            if confidence < blood_smear_confidence_threshold:
                diagnosis_message = "Uncertain: The image could not be reliably classified for malaria. Please upload a clearer blood smear image."
            else:
                diagnosis_message = "Malaria Detected (Parasitized). Please consult a doctor for further evaluation."
        elif class_labels[predicted_class_index] == "Uninfected":
            if confidence < blood_smear_confidence_threshold:
                diagnosis_message = "Uncertain: The image could not be reliably classified for malaria. Please upload a clearer blood smear image."
            else:
                diagnosis_message = "No Malaria Detected (Uninfected)."
        else: # Fallback for any unexpected prediction index
            diagnosis_message = "Unknown diagnosis. Please ensure the model and class labels are correctly configured."
            probability_to_show = None # No meaningful probability for unknown class

        response_data = {
            "diagnosis_message": diagnosis_message,
            "predicted_class_label": class_labels[predicted_class_index] # Useful for debugging/frontend logic
        }
        
        # Only add probability to the response if it's not None
        if probability_to_show is not None:
            response_data["probability"] = round(probability_to_show, 4) # Round for cleaner output

        logging.info(f"Malaria prediction complete: {response_data}")
        return jsonify(response_data)

    except ValueError as e:
        logging.error(f"ValueError during malaria prediction: {e}")
        return jsonify({"error": f"Invalid image data or processing error: {str(e)}"}), 400
    except Exception as e:
        logging.exception(f"An unexpected error occurred during malaria prediction: {e}")
        return jsonify({"error": "An internal server error occurred during prediction. Please try again later."}), 500