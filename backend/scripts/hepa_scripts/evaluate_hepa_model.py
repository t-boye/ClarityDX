import os
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, f1_score
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Paths
# --- UPDATED PATHS IN YOUR EVALUATION SCRIPT (`evaluate_hepa_model.py`) ---
# This BASE_MODELS_DIR should match the one in your training script
BASE_MODELS_DIR = r"C:\Users\USER\Documents\GitHub\Multi-Disease-Diagnosis-System-v0\backend\models"

# Specific file names (these should match what's saved by the training script)
MODEL_FILENAME = "hepatitis_c_model.keras"
SCALER_FILENAME = "hepatitis_c_scaler.pkl" # This should match the renamed scaler file
X_TEST_FILENAME = "X_test_scaled.npy"
Y_TEST_FILENAME = "y_test.npy"

# Construct full paths for loading
MODEL_PATH = os.path.join(BASE_MODELS_DIR, MODEL_FILENAME)
SCALER_PATH = os.path.join(BASE_MODELS_DIR, SCALER_FILENAME)
X_TEST_PATH = os.path.join(BASE_MODELS_DIR, X_TEST_FILENAME)
Y_TEST_PATH = os.path.join(BASE_MODELS_DIR, Y_TEST_FILENAME)

EVAL_REPORT_DIR = "./reports/hepatitis_c_evaluation_plots/"
os.makedirs(EVAL_REPORT_DIR, exist_ok=True)

# Define the category map again for consistent labeling in plots
CATEGORY_MAP = {
    0: 'Blood Donor',
    1: 'Hepatitis',
    2: 'Fibrosis',
    3: 'Cirrhosis'
}


def evaluate_hepatitis_model():
    logging.info("Loading test data (X_test_scaled.npy and y_test.npy)...")
    try:
        X_test_scaled = np.load(X_TEST_PATH)
        y_true = np.load(Y_TEST_PATH)
    except FileNotFoundError:
        logging.error(f"Test data files not found. Please ensure '{X_TEST_PATH}' and '{Y_TEST_PATH}' exist. "
                      "These should be saved by your training script in the correct location.")
        return
    except Exception as e:
        logging.error(f"Error loading test data: {e}")
        return

    logging.info(f"Loaded test data with shape X_test_scaled: {X_test_scaled.shape}, y_true: {y_true.shape}")

    logging.info("Loading trained model...")
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
    except Exception as e:
        logging.error(f"Error loading model from {MODEL_PATH}: {e}. Make sure the model was saved correctly and the path is accurate.")
        return

    logging.info("Predicting on test data...")
    y_pred_probs = model.predict(X_test_scaled, verbose=0)
    y_pred = np.argmax(y_pred_probs, axis=-1)

    # Get unique classes present in the true labels for robust reporting
    unique_classes_true = np.unique(y_true)
    target_names = [CATEGORY_MAP.get(i, f"Class {i}") for i in sorted(unique_classes_true)]

    # Evaluation Metrics
    logging.info("Generating evaluation metrics...")
    
    report = classification_report(y_true, y_pred, target_names=target_names, zero_division=0)
    cm = confusion_matrix(y_true, y_pred)
    f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)

    auc_scores = []
    num_classes = y_pred_probs.shape[1] 
    for i in range(num_classes):
        true_labels_binary = (y_true == i).astype(int)
        if len(np.unique(true_labels_binary)) > 1:
            try:
                auc = roc_auc_score(true_labels_binary, y_pred_probs[:, i])
                auc_scores.append(auc)
            except ValueError as e:
                logging.warning(f"Could not calculate AUC for class {i} (label '{CATEGORY_MAP.get(i, f'Class {i}')}'): {e}. Appending NaN.")
                auc_scores.append(np.nan)
        else:
            logging.info(f"Skipping AUC for class {i} (label '{CATEGORY_MAP.get(i, f'Class {i}')}') due to insufficient samples or only one class present in target (true labels). Appending NaN.")
            auc_scores.append(np.nan)

    mean_auc = np.nanmean(auc_scores) if not np.all(np.isnan(auc_scores)) else np.nan

    logging.info(f"\n📊 Classification Report:\n{report}")
    logging.info(f"🎯 Weighted F1 Score: {f1:.4f}")
    logging.info(f"🚀 Mean AUC Score (excluding uncomputable): {mean_auc:.4f}" if not np.isnan(mean_auc) else "🚀 Mean AUC Score: Not computable or all AUCs were NaN.")

    # Save confusion matrix plot
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=[CATEGORY_MAP.get(i, f"Class {i}") for i in sorted(unique_classes_true)],
                yticklabels=[CATEGORY_MAP.get(i, f"Class {i}") for i in sorted(unique_classes_true)])
    plt.title('Confusion Matrix', fontsize=16)
    plt.xlabel('Predicted Label', fontsize=14)
    plt.ylabel('True Label', fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(EVAL_REPORT_DIR, 'confusion_matrix.png'))
    plt.close()

    logging.info(f"✅ Confusion matrix saved to {EVAL_REPORT_DIR}")
    logging.info("✅ Evaluation complete.")


if __name__ == "__main__":
    evaluate_hepatitis_model()