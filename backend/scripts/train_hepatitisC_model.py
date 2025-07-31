import pandas as pd
import numpy as np
import keras
from keras import backend as K
import tensorflow as tf # Keep for specific TensorFlow operations like tf.cast, tf.one_hot, tf.where

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler
from sklearn.utils.class_weight import compute_class_weight
from imblearn.over_sampling import SMOTE, BorderlineSMOTE
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, f1_score
from sklearn.exceptions import UndefinedMetricWarning
from sklearn.calibration import CalibratedClassifierCV
import warnings
import os
import joblib
import logging

# Suppress warnings
warnings.filterwarnings("ignore", category=UndefinedMetricWarning)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Paths ---
DATA_PATH = r"C:\Users\USER\Documents\GitHub\Multi-Disease-Diagnosis-System-v0\backend\dataset\HepatitisCdata\HepatitisCdata.csv"

# BASE_MODELS_DIR should be the parent 'models' folder
BASE_MODELS_DIR = r"C:\Users\USER\Documents\GitHub\Multi-Disease-Diagnosis-System-v0\backend\models\hepatitis_c_model"

# Specific file names for each artifact
# --- CHANGE HERE: Use .tf extension for SavedModel format ---
MODEL_FILENAME = "hepatitis_c_model.tf"
SCALER_FILENAME = "hepatitis_c_scaler.pkl"
CALIBRATED_MODEL_FILENAME = "calibrated_hepatitis_c_model.joblib"
X_TEST_FILENAME = "X_test_scaled.npy"
Y_TEST_FILENAME = "y_test.npy"
# --- NEW: Filename for storing feature names ---
FEATURE_NAMES_FILENAME = "hepatitis_c_feature_names.pkl"

# Construct full paths by joining base directory and filenames
# Ensure the model path is correctly joined for the .tf directory
MODEL_SAVE_PATH = os.path.join(BASE_MODELS_DIR, MODEL_FILENAME)
SCALER_SAVE_PATH = os.path.join(BASE_MODELS_DIR, SCALER_FILENAME)
CALIBRATED_MODEL_SAVE_PATH = os.path.join(BASE_MODELS_DIR, CALIBRATED_MODEL_FILENAME)
X_TEST_SAVE_PATH = os.path.join(BASE_MODELS_DIR, X_TEST_FILENAME)
Y_TEST_SAVE_PATH = os.path.join(BASE_MODELS_DIR, Y_TEST_FILENAME)
FEATURE_NAMES_SAVE_PATH = os.path.join(BASE_MODELS_DIR, FEATURE_NAMES_FILENAME)


# Define the category map for consistent labeling
CATEGORY_MAP = {
    0: 'Blood Donor',
    1: 'Hepatitis',
    2: 'Fibrosis',
    3: 'Cirrhosis'
}

def load_and_preprocess_data(data_path):
    logging.info("Loading and preprocessing data...")
    df = pd.read_csv(data_path)
    df.drop(columns=['Unnamed: 0'], inplace=True, errors='ignore')

    category_map = {
        '0=Blood Donor': 0, '0s=Blood Donor': 0,
        '1=Hepatitis': 1, '1s=Hepatitis': 1,
        '2=Fibrosis': 2, '2s=Fibrosis': 2,
        '3=Cirrhosis': 3, '3s=Cirrhosis': 3
    }
    df['Category'] = df['Category'].map(category_map)
    
    if df['Category'].isnull().any():
        logging.warning("NaN values found in 'Category' after initial mapping. Dropping rows with NaN 'Category'.")
        df.dropna(subset=['Category'], inplace=True)
        if not df['Category'].empty:
            df['Category'] = df['Category'].astype(int)
        else:
            logging.error("No data remaining after dropping rows with NaN 'Category'. Aborting preprocessing.")
            return None, None, None

    # Map 'Sex' to 0 and 1 to match the frontend's 'm' (0) and 'f' (1) assumption
    # Frontend sends "m" or "f", backend processing assumes 0 or 1 for model training.
    # So, 'm' maps to 0, 'f' maps to 1.
    df['Sex'] = df['Sex'].map({'m': 0, 'f': 1})
    if df['Sex'].isnull().any():
        mode_sex = df['Sex'].mode()[0]
        df['Sex'] = df['Sex'].fillna(mode_sex)
        logging.info(f"Imputed missing values in 'Sex' with mode: {mode_sex}")

    imputation_cols = ['ALB', 'ALP', 'ALT', 'CHOL', 'PROT', 'BIL', 'CHE', 'GGT', 'CREA', 'AST']
    for col in imputation_cols:
        if col in df.columns and df[col].isnull().any():
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            logging.info(f"Imputed missing values in '{col}' with median: {median_val}")

    # --- FEATURE ENGINEERING TO MATCH FRONTEND INPUTS ---
    # Rename for consistency: 'AST/ALT_Ratio' -> 'AST/ALT'
    df['AST/ALT'] = df['AST'] / (df['ALT'] + 1e-7)
    
    # Ensure AgeGroup logic aligns with frontend or is clearly defined
    # Frontend: AgeGroup_Middle (35-55), AgeGroup_Old (55+)
    # Current script: AgeGroup_Middle (30-50), AgeGroup_Old (>50)
    # Let's align them for consistency. Frontend's age groups are:
    # AgeGroup_Middle: 35-55 (inclusive on both ends)
    # AgeGroup_Old: 55+ (greater than or equal to 55)
    df['AgeGroup_Middle'] = ((df['Age'] >= 35) & (df['Age'] <= 55)).astype(int)
    df['AgeGroup_Old'] = (df['Age'] >= 55).astype(int) # This should align with frontend's "55+" being a flag

    # --- REMOVED: Features not sent by the frontend ---
    # df['Age_x_ALB'] = df['Age'] * df['ALB'] # REMOVED
    # df['Sex_x_PROT'] = df['Sex'] * df['PROT'] # REMOVED

    capped_values_count = 0
    numerical_cols_to_cap = ['ALB', 'ALP', 'ALT', 'AST', 'BIL', 'CHE', 'CHOL', 'CREA', 'GGT', 'PROT', 'Age']
    
    for col in numerical_cols_to_cap:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            Q1, Q3 = df[col].quantile([0.25, 0.75])
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            capped_lower_mask = (df[col] < lower_bound)
            capped_upper_mask = (df[col] > upper_bound)
            capped_values_count += capped_lower_mask.sum() + capped_upper_mask.sum()

            df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
            
    logging.info(f"Outlier capping applied. Total {capped_values_count} individual values were capped across specified numerical columns.")

    y = df["Category"].values
    
    # --- SELECT ONLY THE 15 FEATURES THE FRONTEND PROVIDES ---
    # Ensure this list exactly matches the 'formData' keys in your frontend
    frontend_expected_features = [
        "Age", "Sex", "ALB", "ALP", "ALT", "AST", "BIL", "CHE", "CHOL",
        "CREA", "GGT", "PROT", "AST/ALT", "AgeGroup_Middle", "AgeGroup_Old"
    ]
    
    # Filter the DataFrame to include only these specific columns
    X = df[frontend_expected_features]

    for col in X.columns:
        if not pd.api.types.is_numeric_dtype(X[col]):
            logging.warning(f"Column '{col}' is not numeric after preprocessing. Attempting to convert.")
            X[col] = pd.to_numeric(X[col], errors='coerce')
            if X[col].isnull().any():
                X[col] = X[col].fillna(X[col].median())
                logging.info(f"Filled NaNs in '{col}' after numeric conversion.")

    logging.info(f"Final features selected for training: {X.columns.tolist()}")
    logging.info(f"Number of final features: {len(X.columns)}")
    logging.info(f"DataFrame (X) .describe() before converting to numpy array:\n{X.describe().to_string()}")
    logging.info("Data preprocessing complete.")
    return X.values, y, X.columns.tolist() # Return X.columns.tolist() as the definitive feature names

def balance_data(X, y):
    logging.info("Attempting to balance data...")
    class_counts = pd.Series(y).value_counts()
    
    to_remove = class_counts[class_counts < 2].index.tolist()
    if to_remove:
        mask = ~np.isin(y, to_remove)
        X, y = X[mask], y[mask]
        logging.warning(f"Removed classes with less than 2 samples for SMOTE/Stratified Split: {to_remove}")
        class_counts = pd.Series(y).value_counts()

    if len(np.unique(y)) < 2:
        logging.warning("Not enough class diversity (less than 2 unique classes) after removing tiny classes. Skipping SMOTE.")
        return X, y

    min_class_size = np.min(class_counts)
    n_neighbors = min(min_class_size - 1, 5) 
    
    if n_neighbors < 1:
        logging.warning(f"Smallest class has only {min_class_size} samples. Cannot apply SMOTE effectively (k_neighbors would be < 1). Skipping SMOTE.")
        return X, y

    try:
        smote = BorderlineSMOTE(sampling_strategy='not majority', k_neighbors=n_neighbors, random_state=42)
        X_resampled, y_resampled = smote.fit_resample(X, y)
        logging.info(f"Data balanced using BorderlineSMOTE. Original shape: {X.shape}, Resampled shape: {X_resampled.shape}")
    except ValueError as e:
        logging.warning(f"BorderlineSMOTE failed ({e}). Falling back to standard SMOTE.")
        n_neighbors_smote = min(min_class_size - 1, 5) 
        if n_neighbors_smote < 1:
            logging.warning(f"Smallest class still too small for standard SMOTE ({min_class_size} samples). Skipping SMOTE.")
            return X, y

        smote = SMOTE(sampling_strategy='not majority', k_neighbors=n_neighbors_smote, random_state=42)
        X_resampled, y_resampled = smote.fit_resample(X, y)
        logging.info(f"Data balanced using standard SMOTE. Original shape: {X.shape}, Resampled shape: {X_resampled.shape}")

    logging.info(f"Class distribution after balancing: {pd.Series(y_resampled).value_counts().to_dict()}")
    return X_resampled, y_resampled

def prepare_data(X, y, feature_names): # Pass feature_names here
    logging.info("Preparing data for training (splitting and scaling)...")
    
    can_stratify = True
    for cls in np.unique(y):
        if np.sum(y == cls) < 2: 
            can_stratify = False
            break

    if can_stratify:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
        logging.info("Performed stratified train-test split.")
    else:
        logging.warning("Not enough samples per class for true stratified split. Performing non-stratified split.")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = RobustScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    joblib.dump(scaler, SCALER_SAVE_PATH)
    logging.info(f"Scaler saved to {SCALER_SAVE_PATH}")
    
    # --- NEW: Save feature names list ---
    joblib.dump(feature_names, FEATURE_NAMES_SAVE_PATH)
    logging.info(f"Feature names saved to {FEATURE_NAMES_SAVE_PATH}")

    logging.info(f"X_train_scaled .describe() stats:\n{pd.DataFrame(X_train_scaled).describe().to_string()}")
    logging.info("Data preparation complete.")
    return X_train_scaled, X_test_scaled, y_train, y_test

def compute_weights(y):
    logging.info("Computing class weights...")
    classes = np.unique(y)
    if len(classes) == 0:
        logging.warning("No classes found to compute weights for. Returning empty dict.")
        return {}
    if len(classes) == 1:
        logging.warning("Only one unique class found. Class weights will be uniform (1.0).")
        return {classes[0]: 1.0}
    weights = compute_class_weight('balanced', classes=classes, y=y)
    class_weights_dict = dict(zip(classes, weights))
    logging.info(f"Computed class weights: {class_weights_dict}")
    return class_weights_dict

def focal_loss(gamma=2.0, alpha=0.25):
    """
    Focal loss for multi-class classification.
    gamma: Focusing parameter.
    alpha: Class balancing parameter.
    """
    def focal_loss_fixed(y_true, y_pred):
        epsilon = K.epsilon()
        y_pred = K.clip(y_pred, epsilon, 1. - epsilon)

        y_true = tf.cast(y_true, tf.int32)
        y_true_one_hot = tf.one_hot(y_true, K.int_shape(y_pred)[-1])

        cross_entropy = -y_true_one_hot * K.log(y_pred)
        
        pt = tf.where(y_true_one_hot > 0, y_pred, 1 - y_pred)
        
        alpha_factor = tf.where(y_true_one_hot > 0, alpha, 1 - alpha)
        
        focal_weight = alpha_factor * K.pow((1 - pt), gamma)
        
        loss = focal_weight * cross_entropy
        return K.sum(loss, axis=-1)
    
    focal_loss_fixed.__name__ = "focal_loss_fixed" 
    return focal_loss_fixed

keras.utils.get_custom_objects().update({'focal_loss_fixed': focal_loss(gamma=2.0, alpha=0.25)})


def build_model(input_dim, num_classes, use_label_smoothing=False, use_focal_loss=False):
    logging.info(f"Building model with input_dim={input_dim}, num_classes={num_classes}...")
    model = keras.Sequential([
        keras.layers.Dense(256, activation='relu', input_shape=(input_dim,)),
        keras.layers.BatchNormalization(),
        keras.layers.Dropout(0.5),
        keras.layers.Dense(128, activation='relu'),
        keras.layers.BatchNormalization(),
        keras.layers.Dropout(0.4),
        keras.layers.Dense(64, activation='relu'),
        keras.layers.BatchNormalization(),
        keras.layers.Dropout(0.3),
        keras.layers.Dense(num_classes, activation='softmax')
    ])
    
    optimizer = keras.optimizers.AdamW(learning_rate=0.0001, weight_decay=0.0001) 

    if use_focal_loss:
        loss_fn = focal_loss(gamma=2.0, alpha=0.25) 
        logging.info("Using Focal Loss.")
    elif use_label_smoothing:
        loss_fn = keras.losses.SparseCategoricalCrossentropy(from_logits=False, label_smoothing=0.1)
        logging.info("Using Sparse Categorical Crossentropy with Label Smoothing.")
    else:
        loss_fn = keras.losses.SparseCategoricalCrossentropy(from_logits=False)
        logging.info("Using Sparse Categorical Crossentropy (default).")
    
    model.compile(optimizer=optimizer, loss=loss_fn, metrics=['accuracy'])
    logging.info("Model compiled.")
    return model

def train_and_evaluate(model, X_train, y_train, X_test, y_test, class_weights, num_classes):
    logging.info("Starting model training and evaluation...")
    
    callbacks = [
        keras.callbacks.EarlyStopping(monitor='val_loss', patience=20, restore_best_weights=True),
        keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=10, min_lr=1e-7, verbose=1),
        keras.callbacks.ModelCheckpoint(filepath=MODEL_SAVE_PATH, save_best_only=True, monitor='val_loss', mode='min', verbose=1, save_format='tf')
    ]

    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        batch_size=32,
        epochs=200,
        callbacks=callbacks,
        class_weight=class_weights,
        verbose=2
    )

    logging.info("Model training complete. Loading best weights.")
    try:
        loaded_model = keras.models.load_model(MODEL_SAVE_PATH, custom_objects={'focal_loss_fixed': focal_loss(gamma=2.0, alpha=0.25)})
    except Exception as e:
        logging.error(f"Error loading model from {MODEL_SAVE_PATH}: {e}. Falling back to in-memory model (may not be best weights).")
        loaded_model = model

    y_pred_probs = loaded_model.predict(X_test, verbose=0)
    y_pred = np.argmax(y_pred_probs, axis=-1)

    # --- Saving test set for consistent evaluation ---
    logging.info("Saving test set for consistent evaluation...")
    np.save(X_TEST_SAVE_PATH, X_test)
    np.save(Y_TEST_SAVE_PATH, y_test)
    logging.info(f"Test set saved to {X_TEST_SAVE_PATH} and {Y_TEST_SAVE_PATH}")
    # --- End of saving test set ---

    report = classification_report(y_test, y_pred, zero_division=0, output_dict=True)
    conf_matrix = confusion_matrix(y_test, y_pred)
    weighted_f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)

    # --- Calibrated Classifier ---
    logging.info("Starting calibration of the model...")
    class KerasClassifierWrapper:
        def __init__(self, model_keras):
            self.model_keras = model_keras
        
        def predict_proba(self, X):
            return self.model_keras.predict(X, verbose=0)
        
        def fit(self, X, y=None, sample_weight=None):
            pass # Keras model is already fitted, CalibratedClassifierCV uses predict_proba

    keras_wrapper = KerasClassifierWrapper(loaded_model)
    
    calibrated_model = CalibratedClassifierCV(keras_wrapper, method='isotonic', cv="prefit") # "prefit" works if model is already trained

    # For 'prefit' method, you typically use a separate calibration dataset
    # If using X_train for calibration, be aware of potential overfitting to calibration set
    # A common approach is to split X_train further into training and calibration.
    # For simplicity, fitting on X_train for now, but be mindful for production.
    try:
        calibrated_model.fit(X_train, y_train) # Fit calibration on training data
        joblib.dump(calibrated_model, CALIBRATED_MODEL_SAVE_PATH)
        logging.info(f"Calibrated model saved to {CALIBRATED_MODEL_SAVE_PATH}")
        
        y_pred_probs_calibrated = calibrated_model.predict_proba(X_test) # Predict on test set
        y_pred_calibrated = np.argmax(y_pred_probs_calibrated, axis=-1)
        
        calibrated_report = classification_report(y_test, y_pred_calibrated, zero_division=0, output_dict=True)

        logging.info("\n📊 Calibrated Classification Report:")
        for cls, metrics in calibrated_report.items():
            if str(cls).isdigit():
                logging.info(f" Class {CATEGORY_MAP.get(int(cls), f'Class {cls}')}: Precision={metrics['precision']:.2f}, Recall={metrics['recall']:.2f}, F1-Score={metrics['f1-score']:.2f}, Support={metrics['support']}")
            else:
                logging.info(f" {cls.capitalize()}: {metrics:.2f}" if isinstance(metrics, float) else f" {cls.capitalize()}: {metrics}")
        logging.info("\n📉 Calibrated Confusion Matrix:\n" + str(confusion_matrix(y_test, y_pred_calibrated)))
        logging.info(f"🎯 Calibrated Weighted F1 Score: {f1_score(y_test, y_pred_calibrated, average='weighted', zero_division=0):.4f}")

        confidence_threshold = 0.90
        if 2 in CATEGORY_MAP.keys() and CATEGORY_MAP[2] == 'Fibrosis' and 2 in np.unique(y_test):
            confident_fibrosis_indices = np.where((y_pred_calibrated == 2) & (y_pred_probs_calibrated[:, 2] >= confidence_threshold))[0]
            logging.info(f"\n✨ Samples classified as Fibrosis (Class {CATEGORY_MAP.get(2, '2')}) with >= {confidence_threshold*100}% confidence: {len(confident_fibrosis_indices)} samples.")
            if len(confident_fibrosis_indices) > 0:
                logging.info(f"Example confident sample indices: {confident_fibrosis_indices[:min(len(confident_fibrosis_indices), 5)]}")
        else:
            logging.info(f"\n✨ Class 'Fibrosis' (2) not defined or not present in the test set to evaluate confident predictions.")

    except Exception as e:
        logging.error(f"Error during calibration: {e}. Calibration skipped. Consider retraining CalibratedClassifierCV with a different `cv` strategy (e.g., 'stratified_kfold') if prefit is problematic, or ensure `X_train` has enough samples for fitting.")
        y_pred_probs_calibrated = y_pred_probs # Fallback if calibration failed.
    
    auc_scores = []
    for i in range(num_classes):
        true_labels_binary = (y_test == i).astype(int)
        if len(np.unique(true_labels_binary)) > 1:
            try:
                current_y_pred_probs = y_pred_probs_calibrated if 'y_pred_probs_calibrated' in locals() else y_pred_probs
                auc_scores.append(roc_auc_score(true_labels_binary, current_y_pred_probs[:, i]))
            except ValueError as e:
                logging.warning(f"Could not calculate AUC for class {CATEGORY_MAP.get(i, f'Class {i}')}: {e}. Appending NaN.")
                auc_scores.append(np.nan)
        else:
            logging.info(f"Skipping AUC for class {CATEGORY_MAP.get(i, f'Class {i}')} due to insufficient samples or only one class present in target for binary AUC calculation. Appending NaN.")
            auc_scores.append(np.nan)

    mean_auc = np.nanmean(auc_scores) if not np.all(np.isnan(auc_scores)) else np.nan

    logging.info("\n📊 Uncalibrated Classification Report:")
    for cls, metrics in report.items():
        if str(cls).isdigit():
            logging.info(f" Class {CATEGORY_MAP.get(int(cls), f'Class {cls}')}: Precision={metrics['precision']:.2f}, Recall={metrics['recall']:.2f}, F1-Score={metrics['f1-score']:.2f}, Support={metrics['support']}")
        else:
            logging.info(f" {cls.capitalize()}: {metrics:.2f}" if isinstance(metrics, float) else f" {cls.capitalize()}: {metrics}")

    logging.info("\n📉 Confusion Matrix (Uncalibrated):\n" + str(conf_matrix))
    logging.info(f"🎯 Weighted F1 Score (Uncalibrated): {weighted_f1:.4f}")
    logging.info(f"🚀 Mean AUC Score (excluding uncomputable): {mean_auc:.4f}" if not np.isnan(mean_auc) else "🚀 Mean AUC Score: Not computable or all AUCs were NaN.")
    logging.info(f"✅ Best uncalibrated model saved to {MODEL_SAVE_PATH}")
    logging.info("✅ Evaluation complete.")


if __name__ == "__main__":
    # --- Ensure the base models directory exists at the very beginning ---
    os.makedirs(BASE_MODELS_DIR, exist_ok=True)
    logging.info(f"Ensured base models directory exists: {BASE_MODELS_DIR}")

    # --- STEP 1: Load and Preprocess Data ---
    # Pass 'feature_names' to prepare_data
    X, y, feature_names = load_and_preprocess_data(DATA_PATH)
    if X is None:
        logging.error("Data loading and preprocessing failed. Exiting.")
        exit()

    logging.info(f"Initial class distribution: {pd.Series(y).value_counts().to_dict()}")
    
    # --- STEP 2: Balance Data ---
    X_resampled, y_resampled = balance_data(X, y)
    
    num_classes_after_balancing = len(np.unique(y_resampled))
    if num_classes_after_balancing < 2:
        logging.error("⚠️ Not enough class diversity to train the model after balancing. Aborting training.")
        exit()

    # --- STEP 3: Prepare Data (Split and Scale) ---
    # Pass 'feature_names' to prepare_data here
    X_train_scaled, X_test_scaled, y_train, y_test = prepare_data(X_resampled, y_resampled, feature_names) 
    
    # --- STEP 4: Compute Class Weights ---
    if len(np.unique(y_train)) < 2:
        logging.error("Not enough class diversity in training set for class weight computation. Aborting.")
        exit()
    class_weights = compute_weights(y_train)

    # --- STEP 5: Build and Train Model ---
    model = build_model(X_train_scaled.shape[1], num_classes_after_balancing, use_focal_loss=False) 
    model.summary(print_fn=logging.info) 
    
    train_and_evaluate(model, X_train_scaled, y_train, X_test_scaled, y_test, class_weights, num_classes_after_balancing)
    logging.info("✅ Training and full evaluation complete.")