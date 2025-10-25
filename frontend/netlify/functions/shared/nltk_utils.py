import os
import logging
import nltk

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_nltk_data(download_dir):
    """
    Downloads required NLTK data packages into the specified directory.

    Args:
        download_dir (str): The directory where NLTK data will be downloaded.
    """
    # Temporarily add this directory to NLTK's search path for this session
    nltk.data.path.insert(0, download_dir)

    required_packages = {
        'wordnet': 'corpora/wordnet',
        'omw-1.4': 'corpora/omw-1.4',
        'stopwords': 'corpora/stopwords',
        'punkt': 'tokenizers/punkt',
    }

    logger.info(f"Starting NLTK data download check into: {download_dir}")
    for package_name, package_path in required_packages.items():
        try:
            # Check if already downloaded in the specified or default paths
            nltk.data.find(package_path)
            logger.info(f"NLTK package '{package_name}' already downloaded.")
        except LookupError:
            logger.info(f"NLTK package '{package_name}' not found. Downloading to {download_dir}...")
            try:
                nltk.download(package_name, download_dir=download_dir)
                logger.info(f"NLTK package '{package_name}' downloaded successfully.")
            except Exception as e:
                logger.error(f"Failed to download NLTK package '{package_name}': {e}")
                raise

    logger.info("NLTK data download check complete.")

# Normalizer initialization
_normalizer_initialized = False
_normalize_symptom_name_func = None  # Will store the actual function

def get_symptom_normalizer():
    """
    Returns the symptom normalization function.
    Ensures NLTK data and necessary components are ready.

    Returns:
        function: The normalization function for symptom names.
    """
    global _normalizer_initialized, _normalize_symptom_name_func
    if _normalizer_initialized:
        return _normalize_symptom_name_func

    try:
        # These imports happen here because they rely on NLTK data
        from nltk.corpus import stopwords
        from nltk.stem import WordNetLemmatizer
        import re
        import pandas as pd  # Needed for pd.isna in clean_text

        lemmatizer = WordNetLemmatizer()
        stop_words = set(stopwords.words('english'))

        SYMPTOM_SYNONYMS = {
            "high temperature": "fever",
            "pyrexia": "fever",
            "muscle ache": "myalgia",
            "running nose": "runny nose",
            "running_nose": "runny nose",
            "throwing up": "vomiting",
            "joint pain": "arthralgia",
            "head ache": "headache",
            "high_fever": "fever",
        }

        def clean_text_internal(text):
            if pd.isna(text) or text is None:
                return None
            text = str(text).lower()
            text = re.sub(r'[^a-z0-9\s]', '', text)
            text = re.sub(r'\s+', ' ', text).strip()
            return text

        def lemmatize_and_remove_stopwords_internal(text: str):
            tokens = nltk.word_tokenize(text)
            tokens = [lemmatizer.lemmatize(t) for t in tokens if t not in stop_words]
            return ' '.join(tokens)

        def normalize_symptom_name_internal(symptom_name):
            if not symptom_name:
                return None
            cleaned = clean_text_internal(symptom_name.replace('_', ' '))
            if not cleaned:
                return None
            lemmatized = lemmatize_and_remove_stopwords_internal(cleaned)
            return SYMPTOM_SYNONYMS.get(lemmatized, lemmatized)

        _normalize_symptom_name_func = normalize_symptom_name_internal
        _normalizer_initialized = True
        logger.info("Symptom normalizer initialized successfully.")
        return _normalize_symptom_name_func

    except LookupError as e:
        logger.error(f"NLTK data missing for normalizer: {e}. Ensure NLTK data is downloaded correctly.")
        raise
    except Exception as e:
        logger.error(f"Error initializing symptom normalizer: {e}")
        raise
