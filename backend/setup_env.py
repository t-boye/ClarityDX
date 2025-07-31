import os
import sys
import logging
import subprocess
import nltk
import zipfile

# Add the backend directory to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def install_packages(packages):
    """Install required packages using pip."""
    for pkg in packages:
        logger.info(f"Installing {pkg} into current environment...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

def download_nltk_data_to_path(data_path):
    """Download required NLTK data into specified directory."""
    nltk_data_packages = ['wordnet', 'omw-1.4', 'stopwords', 'punkt']
    os.makedirs(data_path, exist_ok=True)
    logger.info(f"📦 Downloading NLTK packages into '{data_path}'...")
    for pack in nltk_data_packages:
        try:
            nltk.download(pack, download_dir=data_path)
            logger.info(f"✅ Downloaded NLTK package: {pack} into {data_path}")
        except Exception as e:
            logger.error(f"❌ Failed to download NLTK package {pack} into {data_path}: {e}")

def extract_corpora_zips(nltk_data_dir):
    """Extract any .zip corpora in the given nltk_data/corpora directory."""
    corpora_dir = os.path.join(nltk_data_dir, 'corpora')
    if not os.path.exists(corpora_dir):
        logger.warning(f"⚠️ No corpora directory found in {nltk_data_dir}")
        return
    for fname in os.listdir(corpora_dir):
        if fname.endswith('.zip'):
            zip_path = os.path.join(corpora_dir, fname)
            extract_dir = os.path.join(corpora_dir, fname.replace('.zip', ''))
            if not os.path.exists(extract_dir):  # avoid re-extract
                logger.info(f"📂 Extracting {zip_path} to {extract_dir}...")
                try:
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(extract_dir)
                    logger.info(f"✅ Extracted {fname}")
                except Exception as e:
                    logger.error(f"❌ Failed to extract {fname}: {e}")
            else:
                logger.info(f"ℹ️ {extract_dir} already exists, skipping extraction.")

def setup_application_environment():
    logger.info("🚀 Starting application environment setup...")

    backend_dir = os.path.dirname(os.path.abspath(__file__))

    # Path for nltk_data inside backend
    project_nltk_data_dir = os.path.join(backend_dir, 'nltk_data')
    os.makedirs(project_nltk_data_dir, exist_ok=True)
    logger.info(f"Ensured project NLTK data directory exists: {project_nltk_data_dir}")

    # Path for nltk_data inside venv
    venv_dir = os.path.join(backend_dir, 'venv')
    venv_nltk_data_dir = os.path.join(venv_dir, 'nltk_data')
    os.makedirs(venv_nltk_data_dir, exist_ok=True)
    logger.info(f"Ensured venv NLTK data directory exists: {venv_nltk_data_dir}")

    # --- Install required Python packages into venv ---
    required_packages = [
        'nltk', 'pydantic', 'flask', 'flask-cors',
        'flask-sqlalchemy', 'flask-migrate', 'python-dotenv',
        'joblib', 'pandas', 'scikit-learn'
    ]
    install_packages(required_packages)

    # --- Download NLTK data into BOTH locations ---
    download_nltk_data_to_path(project_nltk_data_dir)
    download_nltk_data_to_path(venv_nltk_data_dir)

    # --- Extract corpora zips automatically ---
    extract_corpora_zips(project_nltk_data_dir)
    extract_corpora_zips(venv_nltk_data_dir)

    # Ensure backend/models/symScan directory exists
    symScan_models_dir = os.path.join(backend_dir, 'models', 'symScan')
    os.makedirs(symScan_models_dir, exist_ok=True)
    logger.info(f"Ensured model directory exists: {symScan_models_dir}")

    # --- Run SymScan Training Script ---
    train_script_path = os.path.join(backend_dir, 'scripts', 'train_symScan.py')
    if os.path.exists(train_script_path):
        try:
            logger.info("▶ Running SymScan model training script...")
            result = subprocess.run(
                [sys.executable, train_script_path],
                capture_output=True,
                text=True,
                check=True
            )
            logger.info("✅ SymScan training script output:\n" + result.stdout)
            if result.stderr:
                logger.warning("⚠️ SymScan training script warnings:\n" + result.stderr)
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ SymScan training script failed:\n{e.stderr}")
            sys.exit(1)
    else:
        logger.warning(f"⚠️ SymScan training script not found at {train_script_path}. Skipping training.")

    logger.info("✅ Application environment setup complete.")
    logger.info(f"👉 NLTK data installed and extracted in:\n  • {project_nltk_data_dir}\n  • {venv_nltk_data_dir}")

if __name__ == "__main__":
    setup_application_environment()
