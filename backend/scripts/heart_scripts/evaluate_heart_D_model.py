import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import tensorflow as tf
import numpy as np
import joblib # For loading scaler, PCA, feature names, and potentially PolynomialFeatures
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Paths (MUST match your training setup and saved model/artifacts) ---
dataset_path = "./dataset/Heart-Disease/heart.csv" # Original dataset path

# --- THIS IS THE CRITICAL PART: This directory MUST match where your TRAINING script saved the files ---
model_artifacts_dir = "./models/heart_disease_model_advanced/" # <--- MAKE SURE THIS MATCHES YOUR TRAINING SCRIPT'S model_save_dir

# Construct full paths using this base directory
model_load_path = os.path.join(model_artifacts_dir, "heart_disease_model_advanced.h5") # <--- And this .h5 filename
scaler_load_path = os.path.join(model_artifacts_dir, "heart_disease_scaler.pkl")
pca_load_path = os.path.join(model_artifacts_dir, "heart_disease_pca.pkl")
feature_names_load_path = os.path.join(model_artifacts_dir, "heart_disease_feature_names.pkl")
poly_features_load_path = os.path.join(model_artifacts_dir, "heart_disease_polynomial_features.pkl") # New: Path for saved PolynomialFeatures object

# Directory for saving evaluation plots
eval_plots_save_dir = "./reports/heart_disease_evaluation_plots/"
os.makedirs(eval_plots_save_dir, exist_ok=True)
logging.info(f"Evaluation plots save directory created: {eval_plots_save_dir}")


# --- Load Dataset ---
try:
    data = pd.read_csv(dataset_path)
    logging.info(f"Dataset loaded from {dataset_path}. Shape: {data.shape}")
except FileNotFoundError:
    logging.error(f"❌ Dataset file not found: {dataset_path}. Check the path.")
    raise FileNotFoundError(f"❌ Dataset file not found: {dataset_path}. Check the path.")

# --- Data Preprocessing: Missing Values (if any) ---
initial_rows = data.shape[0]
data = data.dropna()
if data.shape[0] < initial_rows:
    logging.warning(f"Dropped {initial_rows - data.shape[0]} rows due to missing values.")
else:
    logging.info("No missing values found in the dataset.")

# --- Feature Engineering (MUST be identical to training script, using loaded objects) ---
logging.info("Starting feature engineering (evaluation mode)...")

# 1. Interaction Features
data['age_chol_interaction'] = data['age'] * data['chol']
data['cp_thalach_interaction'] = data['cp'] * data['thalach']
logging.info("Added interaction features.")

# 2. Polynomial Features for key numerical columns
numerical_cols_for_poly = ['age', 'chol', 'thalach', 'oldpeak']

# Load the PolynomialFeatures object
try:
    poly = joblib.load(poly_features_load_path)
    logging.info("PolynomialFeatures object loaded.")
    # Drop original numerical columns before adding polynomial features
    # Ensure these columns exist before dropping
    cols_to_drop = [col for col in numerical_cols_for_poly if col in data.columns]
    if cols_to_drop:
        data_numerical_subset = data[cols_to_drop] # Extract the subset to transform
        data = data.drop(columns=cols_to_drop) # Drop original columns from main DataFrame
    else:
        logging.warning("Numerical columns for polynomial features not found in data. Skipping original column drop.")
        data_numerical_subset = pd.DataFrame(index=data.index) # Create empty df for transformation if no columns

    poly_features = poly.transform(data_numerical_subset) # Transform using loaded poly object
    poly_feature_names = poly.get_feature_names_out(numerical_cols_for_poly)
    poly_df = pd.DataFrame(poly_features, columns=poly_feature_names, index=data.index)
    data = pd.concat([data, poly_df], axis=1)
    logging.info(f"Added polynomial features. Current shape: {data.shape}")
except FileNotFoundError:
    logging.error(f"❌ PolynomialFeatures file not found: {poly_features_load_path}. Cannot perform identical polynomial feature engineering.")
    logging.warning("Proceeding without polynomial features. Model prediction might be inaccurate.")
    # If PolynomialFeatures cannot be loaded, handle gracefully or raise error
    # For now, we'll proceed, but the model will receive different features
    # This scenario highlights the importance of saving all transformers.

# 3. Age Binning
# Ensure 'age' column exists before binning
if 'age' in data.columns:
    bins = [0, 40, 50, 60, 70, 100]
    labels = [0, 1, 2, 3, 4]
    data['age_group'] = pd.cut(data['age'], bins=bins, labels=labels, right=False)
    data['age_group'] = data['age_group'].astype(float)
    logging.info("Added age binning feature.")
else:
    logging.warning("'age' column not found for age binning. Skipping age binning feature.")


# --- Separate Features (X) and Target (y) after Feature Engineering ---
if 'target' in data.columns:
    X = data.drop("target", axis=1)
    y = data["target"].values
else:
    logging.error("❌ 'target' column not found in the dataset. Cannot proceed with evaluation.")
    raise ValueError("Target column 'target' not found.")

logging.info(f"Features (X) shape after engineering: {X.shape}")
logging.info(f"Target (y) shape: {y.shape}")

# Load feature names saved during training to ensure column order and presence
try:
    trained_feature_names = joblib.load(feature_names_load_path)
    # Check if all required features are present in the current X DataFrame
    missing_features = [col for col in trained_feature_names if col not in X.columns]
    if missing_features:
        logging.error(f"❌ Missing features in current data: {missing_features}. Feature engineering may not be identical to training.")
        # Attempt to fill missing columns with zeros or a sensible default
        for feature in missing_features:
            X[feature] = 0.0 # Or np.nan, or median, depending on strategy
        logging.warning("Filled missing features with zeros. Results may be affected.")

    # Reindex X to match the order of features seen during training
    X = X[trained_feature_names]
    logging.info("Reindexed features to match training order.")
except FileNotFoundError:
    logging.error(f"❌ Feature names file not found: {feature_names_load_path}. Cannot ensure correct feature order.")
    logging.warning("Proceeding without feature name reindexing. Results may be incorrect if feature order differs.")
except KeyError as e:
    logging.error(f"❌ Mismatch in feature names during reindexing: {e}. Check if feature engineering is identical.")
    logging.warning("Proceeding with potential feature mismatch. Results may be incorrect.")
except Exception as e:
    logging.error(f"An unexpected error occurred during feature reindexing: {e}")
    logging.warning("Proceeding with potential feature mismatch. Results may be incorrect.")


# --- Split Data (MUST be identical to training script for correct test set) ---
# Use the same random_state and stratify to get the exact same test set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
logging.info(f"Data split to identify the test set. Test set shape: {X_test.shape}")

# --- Load Scaler and PCA (if used) ---
try:
    scaler = joblib.load(scaler_load_path)
    logging.info("StandardScaler loaded.")
except FileNotFoundError:
    logging.error(f"❌ Scaler file not found: {scaler_load_path}. Cannot scale features.")
    raise FileNotFoundError("❌ Scaler file not found. Evaluation cannot proceed.")

# Apply scaler to the test set
X_test_scaled = scaler.transform(X_test)
logging.info("Test features scaled using loaded StandardScaler.")

# Check if PCA was used during training and load it
USE_PCA = False # Default assumption, will be overridden if pca_load_path exists
if os.path.exists(pca_load_path):
    try:
        pca = joblib.load(pca_load_path)
        USE_PCA = True
        logging.info("PCA object loaded.")
    except Exception as e:
        logging.error(f"❌ Error loading PCA object from {pca_load_path}: {e}. Proceeding without PCA.")

if USE_PCA:
    X_test_final = pca.transform(X_test_scaled)
    logging.info(f"PCA applied to test features. Reduced dimensions from {X_test_scaled.shape[1]} to {X_test_final.shape[1]}.")
else:
    X_test_final = X_test_scaled
    logging.info("PCA skipped (or not used in training). Using scaled features directly.")

# Convert to float32 for TensorFlow compatibility
X_test_final = X_test_final.astype(np.float32)
y_test = y_test.astype(np.float32)
logging.info("Converted test data to float32 for TensorFlow.")


# --- Load Trained Model ---
try:
    # Compile=False is sometimes used for faster loading if you only need predict/evaluate
    # but for full robustness, it's better to load with compile=True if compiled with custom objects/metrics
    model = tf.keras.models.load_model(model_load_path, compile=True)
    logging.info(f"Model loaded successfully from {model_load_path}.")
    model.summary(print_fn=logging.info) # Log model summary
except Exception as e:
    logging.error(f"❌ Error loading model: {e}. Check model path and file integrity.")
    raise FileNotFoundError(f"❌ Model file not found or corrupted: {model_load_path}. Evaluation cannot proceed.")

# --- Evaluate Model ---
logging.info("Starting model evaluation on the test set...")
y_pred_proba = model.predict(X_test_final)
y_pred = (y_pred_proba > 0.5).astype(int) # Convert probabilities to binary predictions

# Define target names explicitly to avoid issues with float/int labels
target_names = ['No Heart Disease', 'Heart Disease']

# Calculate Core Metrics
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred, target_names=target_names, output_dict=True)
cm = confusion_matrix(y_test, y_pred)

logging.info("\n" + "="*40)
logging.info("⭐ Model Performance Metrics ⭐")
logging.info("="*40)
logging.info(f"🚀 Overall Accuracy: {accuracy:.4f}")
logging.info("\n📊 Classification Report:")
logging.info(f"{classification_report(y_test, y_pred, target_names=target_names)}") # Print the pretty formatted report

# Extract specific metrics for "Heart Disease" (positive class, typically 1)
# Ensure to access keys as strings for output_dict
precision_hd = report['Heart Disease']['precision']
recall_hd = report['Heart Disease']['recall']
f1_hd = report['Heart Disease']['f1-score']

logging.info(f"  Precision (Heart Disease): {precision_hd:.4f}")
logging.info(f"  Recall (Heart Disease): {recall_hd:.4f}")
logging.info(f"  F1-Score (Heart Disease): {f1_hd:.4f}")

# --- Confusion Matrix Details ---
logging.info("\n" + "="*40)
logging.info("🔢 Confusion Matrix Breakdown 🔢")
logging.info("="*40)

# Extract specific values for the table format:
# | | Predicted No Heart Disease | Predicted Heart Disease |
# | :-------------- | :------------------------- | :---------------------- |
# | Actual No Heart Disease | [TN value]                 | [FP value]              |
# | Actual Heart Disease | [FN value]                 | [TP value]              |

TN = cm[0, 0] # True Negatives (No Heart Disease correctly identified)
FP = cm[0, 1] # False Positives (No Heart Disease misclassified as Heart Disease)
FN = cm[1, 0] # False Negatives (Heart Disease misclassified as No Heart Disease)
TP = cm[1, 1] # True Positives (Heart Disease correctly identified)

logging.info(f"  True Positives (TP): {TP} - (Correctly predicted Heart Disease)")
logging.info(f"  False Negatives (FN): {FN} - (Actual Heart Disease, predicted No Heart Disease)")
logging.info(f"  False Positives (FP): {FP} - (Actual No Heart Disease, predicted Heart Disease)")
logging.info(f"  True Negatives (TN): {TN} - (Correctly predicted No Heart Disease)")

# --- Visualize Confusion Matrix ---
plt.figure(figsize=(7, 6)) # Slightly larger figure for better readability
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False,
            xticklabels=target_names,
            yticklabels=target_names)
plt.title('Confusion Matrix for Heart Disease Diagnosis')
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.tight_layout()
plt.savefig(os.path.join(eval_plots_save_dir, 'evaluation_confusion_matrix.png'))
plt.close()
logging.info(f"Confusion matrix plot saved to {eval_plots_save_dir}")

logging.info("\n" + "="*40)
logging.info("✅ Evaluation complete for Heart Disease model.")
logging.info("="*40)