import logging
import os
import io # Needed to handle bytes as an in-memory file
from PIL import Image # Make sure you have 'Pillow' installed: pip install Pillow
import numpy as np # Make sure you have 'numpy' installed: pip install numpy

logger = logging.getLogger(__name__)

# This is the function that the "predict_malaria" function tries to import
# and use. It MUST be defined here.
def process_image(image_data: bytes) -> np.ndarray:
    """
    Processes raw image data (bytes) into a format suitable for a Keras/TensorFlow model.
    This function will typically:
    1. Open the image from bytes.
    2. Resize it to the target dimensions (e.g., 128x128 for Malaria).
    3. Normalize pixel values.
    4. Convert it to a NumPy array with a batch dimension.

    Args:
        image_data (bytes): The raw bytes of the image file.

    Returns:
        np.ndarray: A preprocessed NumPy array (e.g., of shape (1, height, width, channels))
                    ready for model prediction.
    """
    logger.info("Starting image processing from raw bytes in image_processing_service.py.")
    try:
        # Use io.BytesIO to treat bytes data as a file
        image_stream = io.BytesIO(image_data)
        
        # Open the image using Pillow
        with Image.open(image_stream) as img:
            # Convert to RGB (important if images are RGBA or grayscale)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize the image to the expected input size for the Malaria model
            # Assuming a Malaria model expects 128x128 images with 3 color channels
            target_size = (128, 128) 
            img = img.resize(target_size, Image.Resampling.LANCZOS) # or Image.ANTIALIAS for older Pillow

            # Convert the image to a NumPy array
            img_array = np.array(img)
            
            # Normalize pixel values to 0-1 range (common for CNNs)
            img_array = img_array / 255.0
            
            # Add a batch dimension: (height, width, channels) -> (1, height, width, channels)
            processed_image_batch = np.expand_dims(img_array, axis=0)
            
            logger.info(f"Image processed to shape: {processed_image_batch.shape} and type: {processed_image_batch.dtype}")
            return processed_image_batch

    except Exception as e:
        logger.error(f"Error during image processing in image_processing_service.py: {e}", exc_info=True)
        # Re-raise the exception or return an error state that the caller can handle
        raise ValueError(f"Failed to preprocess image data: {str(e)}")

