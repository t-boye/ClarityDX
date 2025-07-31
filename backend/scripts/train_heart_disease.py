import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, StratifiedShuffleSplit
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.utils import class_weight
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, LearningRateScheduler
from tensorflow.keras.optimizers import Adam
import numpy as np
import joblib
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Corrected Paths ---
dataset_path = "./dataset/Heart-Disease/heart.csv" # Using relative path for portability

# Directory for saving model artifacts (adjust as needed, but keep it relative if possible)
model_save_dir = "./models/heart_disease_model_advanced/" # This matches the folder structure you've used before

# Directory for saving plots
plots_save_dir = "./reports/heart_disease_plots_advanced/"

# Ensure directories exist
os.makedirs(model_save_dir, exist_ok=True)
os.makedirs(plots_save_dir, exist_ok=True)

# Define the full path for the Keras model file
model_save_path = os.path.join(model_save_dir, "heart_disease_model_advanced.keras")


# Load dataset
data = pd.read_csv(dataset_path)
logging.info(f"Dataset loaded: {data.shape}")

# Plot class distribution
plt.figure()
sns.countplot(x='target', data=data)
plt.title('Class Distribution')
plt.savefig(os.path.join(plots_save_dir, 'class_distribution.png'))
plt.close()

# Correlation matrix
plt.figure(figsize=(12, 10))
sns.heatmap(data.corr(numeric_only=True), annot=True, fmt=".2f", cmap='coolwarm')
plt.title('Initial Correlation Matrix')
plt.savefig(os.path.join(plots_save_dir, 'initial_correlation_matrix.png'))
plt.close()

# Drop missing values (if any)
data.dropna(inplace=True)

# Separate features (X_original) and target (y) early
X_original_features = data.drop("target", axis=1)
y = data["target"].values
logging.info(f"Initial X_original_features shape: {X_original_features.shape}, y shape: {y.shape}")

# --- Feature Engineering ---
logging.info("Starting feature engineering...")

# Create a copy to perform feature engineering on
X_engineered = X_original_features.copy()

# Interaction features (add to X_engineered)
X_engineered['age_chol_interaction'] = X_engineered['age'] * X_engineered['chol']
X_engineered['cp_thalach_interaction'] = X_engineered['cp'] * X_engineered['thalach']
logging.info(f"Added interaction features. X_engineered shape: {X_engineered.shape}")

# Age binning (add to X_engineered, operating on the existing 'age' column)
bins = [0, 40, 50, 60, 70, 100]
labels = [0, 1, 2, 3, 4]
X_engineered['age_group'] = pd.cut(X_engineered['age'], bins=bins, labels=labels, right=False).astype(float)
logging.info(f"Added age binning. X_engineered shape: {X_engineered.shape}")


# --- CRITICAL STEP: Save the list of feature names BEFORE PolynomialFeatures ---
# This list contains the names of the features *before* polynomial expansion.
# The prediction script will use this list to create the initial DataFrame
# that gets scaled and then passed to PolynomialFeatures.
feature_names_before_poly_and_pca = X_engineered.columns.tolist()
joblib.dump(feature_names_before_poly_and_pca, os.path.join(model_save_dir, "heart_disease_feature_names.pkl"))
logging.info(f"Saved heart_disease_feature_names.pkl with {len(feature_names_before_poly_and_pca)} features.")
logging.info(f"Feature list saved: {feature_names_before_poly_and_pca}") # Added explicit print of the list

# Handle imbalance
class_weights = class_weight.compute_class_weight('balanced', classes=np.unique(y), y=y)
class_weights_dict = {0: class_weights[0], 1: class_weights[1]}

# Split data (use X_engineered for splitting)
X_train, X_test, y_train, y_test = train_test_split(
    X_engineered, y, test_size=0.2, random_state=42, stratify=y)
logging.info(f"Train split X_engineered shape: {X_train.shape}, Test split X_engineered shape: {X_test.shape}")

# --- Scaling ---
# The scaler is fitted on the X_engineered features (original + manual interactions + age groups)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
joblib.dump(scaler, os.path.join(model_save_dir, "heart_disease_scaler.pkl"))
logging.info("StandardScaler fitted and saved.")

# Convert scaled data back to DataFrame to retain column names for PolynomialFeatures.
# This ensures PolynomialFeatures receives data with expected named columns.
X_train_scaled_df = pd.DataFrame(X_train_scaled, columns=X_train.columns, index=X_train.index)
X_test_scaled_df = pd.DataFrame(X_test_scaled, columns=X_test.columns, index=X_test.index)
logging.info(f"Scaled data converted to DataFrame. Columns match original engineered features.")


# --- Polynomial Features (applied AFTER scaling) ---
# This 'poly' object will be saved and used in the prediction script.
# It MUST be fitted on the data that has the same structure (and column names)
# as `scaled_df` in the prediction script.
poly = PolynomialFeatures(degree=2, include_bias=False)
# Identify numerical columns for polynomial features *from the scaled DataFrame*
# This should ideally be a subset of X_engineered.columns that are numerical and make sense for poly features.
# For consistency with your previous script's intent, we'll assume these were the ones
# that you wanted to expand: 'age', 'chol', 'thalach', 'oldpeak'.
# Ensure these columns actually exist in X_engineered / X_train_scaled_df.
numerical_cols_for_poly_expansion = ['age', 'chol', 'thalach', 'oldpeak']

# Ensure these columns are indeed present in the scaled DataFrame for fitting poly features
# (These should be present if they were part of your original features or interaction features)
missing_poly_cols = [col for col in numerical_cols_for_poly_expansion if col not in X_train_scaled_df.columns]
if missing_poly_cols:
    logging.error(f"Error: Columns {missing_poly_cols} intended for PolynomialFeatures are not found in X_train_scaled_df. Please check your feature engineering steps.")
    raise ValueError(f"Missing columns for PolynomialFeatures: {missing_poly_cols}")

X_train_poly = poly.fit_transform(X_train_scaled_df[numerical_cols_for_poly_expansion]) # Fit poly on the *scaled subset*
X_test_poly = poly.transform(X_test_scaled_df[numerical_cols_for_poly_expansion]) # Transform the *scaled subset*
joblib.dump(poly, os.path.join(model_save_dir, "heart_disease_polynomial_features.pkl"))
logging.info(f"PolynomialFeatures fitted and saved. Features before expansion: {len(numerical_cols_for_poly_expansion)}. New features generated by poly: {X_train_poly.shape[1]}")

# Now, we need to combine the polynomial features with the other features that were NOT fed into poly.
# Identify columns that were NOT used for polynomial expansion
cols_not_for_poly = [col for col in X_train_scaled_df.columns if col not in numerical_cols_for_poly_expansion]

# Convert non-poly features to numpy arrays
X_train_non_poly = X_train_scaled_df[cols_not_for_poly].values
X_test_non_poly = X_test_scaled_df[cols_not_for_poly].values

# Concatenate non-poly features with poly features
X_train_combined = np.hstack((X_train_non_poly, X_train_poly))
X_test_combined = np.hstack((X_test_non_poly, X_test_poly))

logging.info(f"Combined features shape for training (after poly): {X_train_combined.shape}")

# --- Optional PCA ---
USE_PCA = True
if USE_PCA:
    pca = PCA(n_components=0.95)
    X_train_final = pca.fit_transform(X_train_combined) # PCA on the combined (non-poly + poly) features
    X_test_final = pca.transform(X_test_combined)
    joblib.dump(pca, os.path.join(model_save_dir, "heart_disease_pca.pkl"))
    logging.info(f"PCA fitted and saved. Reduced dimensions to {X_train_final.shape[1]}")
else:
    X_train_final = X_train_combined
    X_test_final = X_test_combined

# Stratified validation split
sss = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
for train_idx, val_idx in sss.split(X_train_final, y_train):
    X_train_split = X_train_final[train_idx]
    y_train_split = y_train[train_idx]
    X_val_split = X_train_final[val_idx]
    y_val_split = y_train[val_idx]

# Convert to float32 for Keras
X_train_split = X_train_split.astype(np.float32)
y_train_split = y_train_split.astype(np.float32)
X_val_split = X_val_split.astype(np.float32)
y_val_split = y_val_split.astype(np.float32)
X_test_final = X_test_final.astype(np.float32)
y_test = y_test.astype(np.float32)

logging.info(f"Final training data shape for Keras: {X_train_split.shape}")

# Learning rate schedule
def lr_scheduler(epoch, lr):
    if epoch < 10:
        return lr
    elif epoch < 20:
        return lr * 0.9
    else:
        return lr * 0.8

# Model
def create_model(input_dim):
    model = Sequential([
        Dense(256, activation='relu', input_shape=(input_dim,)),
        BatchNormalization(),
        Dropout(0.3),
        Dense(128, activation='relu'),
        BatchNormalization(),
        Dropout(0.3),
        Dense(64, activation='relu'),
        BatchNormalization(),
        Dropout(0.3),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])
    return model

model = create_model(X_train_split.shape[1])
model.summary(print_fn=logging.info)

# Train
early_stopping = EarlyStopping(monitor="val_loss", patience=15, restore_best_weights=True, verbose=1)
lr_callback = LearningRateScheduler(lr_scheduler, verbose=0)

logging.info("Training started...")
history = model.fit(
    X_train_split, y_train_split,
    validation_data=(X_val_split, y_val_split),
    epochs=200,
    batch_size=32,
    class_weight=class_weights_dict,
    callbacks=[early_stopping, lr_callback],
    verbose=1
)

# Evaluate
y_pred_proba = model.predict(X_test_final)
y_pred = (y_pred_proba > 0.5).astype(int)
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)
logging.info(f"Test Accuracy: {accuracy:.4f}")
logging.info(f"\n{report}")

# Save Keras model
model.save(model_save_path)
logging.info(f"Keras model saved to: {model_save_path}")

# Training plots
plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Train Accuracy')
plt.plot(history.history['val_accuracy'], label='Val Accuracy')
plt.title('Accuracy')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Val Loss')
plt.title('Loss')
plt.legend()

plt.tight_layout()
plt.savefig(os.path.join(plots_save_dir, 'training_history.png'))
plt.close()

# Confusion matrix
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['No HD', 'HD'], yticklabels=['No HD', 'HD'])
plt.title('Confusion Matrix')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.tight_layout()
plt.savefig(os.path.join(plots_save_dir, 'confusion_matrix.png'))
plt.close()

logging.info("Training script completed successfully. All artifacts saved.")