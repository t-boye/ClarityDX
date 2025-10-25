"""
Netlify Serverless Function: Malaria Image Processing
Endpoint: /.netlify/functions/process-malaria-image
Method: POST
Accepts: multipart/form-data with image file
"""

import json
import logging
import sys
import os
import base64
import numpy as np
from io import BytesIO

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'shared'))

from model_config import MODEL_URLS
from model_loader import load_models
from services.image_processing_service import process_image as process_malaria_image_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Required model artifacts
REQUIRED_MODELS = [
    'malaria_model'
]


def parse_multipart_form_data(event):
    """
    Parse multipart/form-data from Netlify function event.
    Returns the image data if found.
    """
    try:
        # Check if body is base64 encoded (Netlify automatically encodes binary data)
        is_base64_encoded = event.get('isBase64Encoded', False)
        body = event.get('body', '')

        if is_base64_encoded:
            body = base64.b64decode(body)
        else:
            body = body.encode('utf-8') if isinstance(body, str) else body

        # Get the content type header to find the boundary
        headers = event.get('headers', {})
        content_type = headers.get('content-type') or headers.get('Content-Type', '')

        if 'multipart/form-data' not in content_type:
            return None, "Request must be multipart/form-data"

        # Extract boundary from content-type header
        boundary = None
        for part in content_type.split(';'):
            part = part.strip()
            if part.startswith('boundary='):
                boundary = part.split('=', 1)[1].strip('"')
                break

        if not boundary:
            return None, "No boundary found in Content-Type"

        # Parse multipart data manually
        boundary_bytes = f'--{boundary}'.encode()
        parts = body.split(boundary_bytes)

        for part in parts:
            if b'Content-Disposition' in part and b'name="image"' in part:
                # Find the start of the actual file data (after headers)
                header_end = part.find(b'\r\n\r\n')
                if header_end == -1:
                    continue

                # Extract the file data
                file_data = part[header_end + 4:]

                # Remove trailing CRLF
                if file_data.endswith(b'\r\n'):
                    file_data = file_data[:-2]

                return file_data, None

        return None, "No image field found in form data"

    except Exception as e:
        logger.exception(f"Error parsing multipart data: {e}")
        return None, str(e)


def handler(event, context):
    """Netlify serverless function handler for malaria image processing."""
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}

    try:
        logger.info("Received malaria image processing request")

        # Parse the uploaded image from multipart form data
        image_data, error = parse_multipart_form_data(event)

        if error or not image_data:
            logger.error(f"Failed to parse image: {error}")
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'No valid image file uploaded',
                    'details': error or 'Image field not found',
                    'medical_disclaimer': 'This system is informational only.'
                })
            }

        # Load models
        logger.info("Loading malaria model...")
        models_dict = load_models(MODEL_URLS, REQUIRED_MODELS)

        missing_models = [key for key in REQUIRED_MODELS if key not in models_dict]
        if missing_models:
            logger.error(f"Missing models: {missing_models}")
            return {
                'statusCode': 503,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Malaria model not available',
                    'details': f'Missing: {missing_models}',
                    'medical_disclaimer': 'This system is informational only.'
                })
            }

        # Process the image
        logger.info("Processing uploaded image...")
        processed_image = process_malaria_image_data(image_data)

        # Get predictions
        logger.info("Making prediction...")
        model = models_dict['malaria_model']
        raw_predictions = model.predict(processed_image)

        # Get the predicted class
        predicted_class_index = np.argmax(raw_predictions, axis=1)[0]
        confidence = float(raw_predictions[0][predicted_class_index])

        # Class labels (ensure this matches your model training)
        class_labels = ['Uninfected', 'Parasitized', 'NonBloodSmear']

        # Confidence threshold
        blood_smear_confidence_threshold = 0.7

        # Determine diagnosis message
        predicted_class = class_labels[predicted_class_index]
        probability_to_show = confidence

        if predicted_class == "NonBloodSmear":
            diagnosis_message = "This image is not a blood smear. Please upload a blood smear image."
            probability_to_show = None
        elif predicted_class == "Parasitized":
            if confidence < blood_smear_confidence_threshold:
                diagnosis_message = "Uncertain: The image could not be reliably classified for malaria. Please upload a clearer blood smear image."
            else:
                diagnosis_message = "Malaria Detected (Parasitized). Please consult a doctor for further evaluation."
        elif predicted_class == "Uninfected":
            if confidence < blood_smear_confidence_threshold:
                diagnosis_message = "Uncertain: The image could not be reliably classified for malaria. Please upload a clearer blood smear image."
            else:
                diagnosis_message = "No Malaria Detected (Uninfected)."
        else:
            diagnosis_message = "Unknown diagnosis. Please ensure the model and class labels are correctly configured."
            probability_to_show = None

        # Build response
        response_data = {
            "diagnosis_message": diagnosis_message,
            "predicted_class_label": predicted_class
        }

        if probability_to_show is not None:
            response_data["probability"] = probability_to_show

        response_data["medical_disclaimer"] = "This system is informational only and not a substitute for professional medical advice."

        logger.info(f"Prediction successful: {predicted_class} with confidence {confidence}")

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(response_data)
        }

    except Exception as e:
        logger.exception(f"Error in malaria image processing: {e}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal server error',
                'details': str(e),
                'medical_disclaimer': 'This system is informational only.'
            })
        }
