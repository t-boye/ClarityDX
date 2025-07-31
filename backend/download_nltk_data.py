import nltk
import os

# Define the NLTK data path relative to this script's directory
nltk_data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nltk_data')
if not os.path.exists(nltk_data_path):
    os.makedirs(nltk_data_path)
nltk.data.path.append(nltk_data_path)

# Download the 'wordnet' corpus
try:
    nltk.data.find('corpora/wordnet')
    print("Wordnet corpus already present.")
except nltk.downloader.DownloadError:
    print("Downloading wordnet corpus...")
    nltk.download('wordnet', download_dir=nltk_data_path)
    print("Wordnet download complete.")

# Download the 'omw-1.4' (Open Multilingual Wordnet) corpus, often needed with WordNet
try:
    nltk.data.find('corpora/omw-1.4')
    print("omw-1.4 corpus already present.")
except nltk.downloader.DownloadError:
    print("Downloading omw-1.4 corpus...")
    nltk.download('omw-1.4', download_dir=nltk_data_path)
    print("omw-1.4 download complete.")

print(f"NLTK data stored in: {nltk_data_path}")