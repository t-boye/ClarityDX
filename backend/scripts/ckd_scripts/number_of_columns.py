import os
import pickle

# Render-compatible path configuration
MODEL_DIR = os.path.join('backend', 'models', 'ckd_model')
FEATURE_FILE = 'ckd_feature_names.pkl'
file_path = os.path.join(MODEL_DIR, FEATURE_FILE)

try:
    with open(file_path, 'rb') as f:
        feature_names = pickle.load(f)

    print(f"Successfully loaded feature names from {file_path}")
    print(f"Number of features: {len(feature_names)}")
    print("Feature names:")
    for i, name in enumerate(feature_names, 1):
        print(f"{i}. {name}")

except FileNotFoundError:
    print(f"Error: File not found at {file_path}")
    print("Current working directory:", os.getcwd())
    print("Directory contents:")
    try:
        print(os.listdir(MODEL_DIR))
    except FileNotFoundError:
        print(f"Model directory not found: {MODEL_DIR}")
except Exception as e:
    print(f"An error occurred: {str(e)}")