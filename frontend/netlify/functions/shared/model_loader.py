"""
Model Loading Utility for Netlify Serverless Functions
Handles downloading and caching ML models from S3
"""

import os
import logging
import requests
import joblib
import tensorflow as tf
from io import BytesIO
from typing import Dict, Any, Optional
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global cache for loaded models (persists across warm function invocations)
_MODEL_CACHE: Dict[str, Any] = {}


def download_and_load_joblib(url: str, cache_key: str) -> Any:
    """
    Fetches a joblib artifact from a URL and loads it into memory.
    Uses in-memory caching to avoid re-downloading on warm starts.

    Args:
        url: S3 URL to the model file
        cache_key: Unique key for caching this model

    Returns:
        Loaded model/artifact
    """
    # Check cache first
    if cache_key in _MODEL_CACHE:
        logger.info(f"Using cached model: {cache_key}")
        return _MODEL_CACHE[cache_key]

    try:
        logger.info(f"Downloading joblib artifact from {url}")
        response = requests.get(url, timeout=60)
        response.raise_for_status()

        model = joblib.load(BytesIO(response.content))

        # Cache the loaded model
        _MODEL_CACHE[cache_key] = model
        logger.info(f"Successfully loaded and cached {cache_key}")

        return model
    except Exception as e:
        logger.error(f"Failed to load artifact from {url}: {e}")
        return None


def download_and_load_tensorflow(url: str, cache_key: str) -> Optional[tf.keras.Model]:
    """
    Downloads a TensorFlow model from a URL and loads it.
    Uses file-based caching in /tmp for TensorFlow models.

    Args:
        url: S3 URL to the model file
        cache_key: Unique key for caching this model

    Returns:
        Loaded TensorFlow model
    """
    # Check in-memory cache first
    if cache_key in _MODEL_CACHE:
        logger.info(f"Using cached TensorFlow model: {cache_key}")
        return _MODEL_CACHE[cache_key]

    # Use /tmp directory for serverless environment
    model_filename = os.path.basename(url)
    temp_path = os.path.join("/tmp", f"{cache_key}_{model_filename}")

    # Check if already downloaded to /tmp (survives across warm starts)
    if os.path.exists(temp_path):
        try:
            logger.info(f"Loading TensorFlow model from /tmp: {cache_key}")
            model = tf.keras.models.load_model(temp_path)
            _MODEL_CACHE[cache_key] = model
            return model
        except Exception as e:
            logger.warning(f"Failed to load cached model, re-downloading: {e}")
            os.remove(temp_path)

    # Download the model
    try:
        logger.info(f"Downloading TensorFlow model from {url}")
        response = requests.get(url, timeout=120, stream=True)
        response.raise_for_status()

        # Save to /tmp
        with open(temp_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info(f"Successfully downloaded to {temp_path}")

        # Load the model
        model = tf.keras.models.load_model(temp_path)

        # Cache in memory
        _MODEL_CACHE[cache_key] = model
        logger.info(f"Successfully loaded and cached TensorFlow model: {cache_key}")

        return model
    except Exception as e:
        logger.error(f"Failed to load TensorFlow model from {url}: {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return None


def load_models(model_urls: Dict[str, str], required_keys: list) -> Dict[str, Any]:
    """
    Loads multiple models based on URL configuration.

    Args:
        model_urls: Dictionary mapping model keys to S3 URLs
        required_keys: List of model keys that must be loaded

    Returns:
        Dictionary of loaded models
    """
    loaded_models = {}

    for key in required_keys:
        url = model_urls.get(key)
        if not url:
            logger.error(f"Missing URL for required model: {key}")
            continue

        # Determine file type and load accordingly
        if url.endswith(('.pkl', '.joblib')):
            model = download_and_load_joblib(url, key)
        elif url.endswith(('.h5', '.keras')):
            model = download_and_load_tensorflow(url, key)
        else:
            logger.warning(f"Unsupported file extension for {key}: {url}")
            continue

        if model is not None:
            loaded_models[key] = model
        else:
            logger.error(f"Failed to load required model: {key}")

    return loaded_models


def get_cached_model(cache_key: str) -> Optional[Any]:
    """
    Retrieves a model from the cache if it exists.

    Args:
        cache_key: The cache key for the model

    Returns:
        Cached model or None
    """
    return _MODEL_CACHE.get(cache_key)


def clear_model_cache():
    """Clears the model cache. Useful for testing or manual cache invalidation."""
    global _MODEL_CACHE
    _MODEL_CACHE = {}
    logger.info("Model cache cleared")
