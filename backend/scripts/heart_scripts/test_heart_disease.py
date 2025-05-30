import tensorflow as tf
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from imblearn.over_sampling import SMOTE
import os
import joblib
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from kerastuner.tuners import BayesianOptimization

# Debug: Print current working directory
print("Current Working Directory:", os.getcwd())

# Define the path to the dataset
data_path = "../dataset/Heart-Disease/heart.csv"

# Check if the dataset file exists before proceeding
if not os.path.exists(data_path):
    raise FileNotFoundError(f"❌ Dataset file not found: {data_path}. Check the path.")

# Load dataset
data = pd.read_csv(data_path)
print("✅ Dataset loaded successfully!")

# Handle missing values
data.fillna(data.median(), inplace=True)

# Separate features (X) and target (y)
X = data.drop("target", axis=1)  # Assuming 'target' is the target column
y = data["target"]

# Handle class imbalance using SMOTE
smote = SMOTE()
X_resampled, y_resampled = smote.fit_resample(X, y)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X_resampled, y_resampled, test_size=0.2, random_state=42, stratify=y_resampled)

# Standardize features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Save the scaler
scaler_path = "../models/heart_disease_model"

# Create the directory if it doesn't exist
os.makedirs(os.path.dirname(scaler_path), exist_ok=True)

# Attempt to save the scaler
try:
    joblib.dump(scaler, scaler_path)
    print("✅ Scaler saved successfully!")
except Exception as e:
    print(f"❌ Error saving scaler: {e}")

# Function to create the model
def build_model(hp):
    model = Sequential()
    model.add(Dense(hp.Int('units_1', min_value=32, max_value=128, step=32), activation='relu', input_shape=(X_train.shape[1],)))
    model.add(Dropout(0.5))
    model.add(BatchNormalization())
    model.add(Dense(hp.Int('units_2', min_value=16, max_value=64, step=16), activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(
        optimizer=tf.keras.optimizers.Adam(hp.Choice('learning_rate', values=[1e-2, 1e-3, 1e-4])),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    return model

# Hyperparameter tuning using Bayesian Optimization
tuner = BayesianOptimization(
    build_model,
    objective='val_accuracy',
    max_trials=10,
    executions_per_trial=3,
    directory='tuner_dir',
    project_name='heart_disease_tuning'
)

tuner.search(X_train, y_train, epochs=50, validation_data=(X_test, y_test))

# Get the best model
best_model = tuner.get_best_models(num_models=1)[0]

# Callbacks for early stopping and model checkpointing
checkpoint_path = r"C:/Users/USER/Documents/GitHub/malaria-expert-system/backend/models/heart_disease_model/best_model.h5"
callbacks = [
    EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
    ModelCheckpoint(filepath=checkpoint_path, monitor='val_loss', save_best_only=True)
]

# Train the best model
best_model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=50, callbacks=callbacks)

# Evaluate the model
y_pred = best_model.predict(X_test)
y_pred_classes = (y_pred > 0.5).astype(int)

# Print classification report
print(classification_report(y_test, y_pred_classes))

# Save the best model
best_model.save(checkpoint_path)  # Save the model again to ensure it's saved
print("✅ Model saved successfully!")

# Function to preprocess input data
def preprocess_input(input_data):
    try:
        input_df = pd.DataFrame([input_data], columns=X.columns)
        input_scaled = scaler.transform(input_df)
        return input_scaled
    except Exception as e:
        print("❌ Error in preprocessing input:", e)
        return None

# Function to diagnose heart disease
def diagnose_and_predict_heart_disease(input_data):
    input_scaled = preprocess_input(input_data)
    if input_scaled is None:
        return {"error": "Invalid input data"}
    
    prediction = best_model.predict(input_scaled)
    probability = prediction[0][0]
    
    diagnosis = "Heart Disease" if probability > 0.5 else "No Heart Disease"
    risk_level = "High" if probability > 0.75 else "Moderate" if probability > 0.5 else "Low"
    recommendation = "Consult a healthcare professional." if diagnosis == "Heart Disease" else "Maintain a healthy lifestyle."
    
    return {
        "diagnosis": diagnosis,
        "probability": probability,
        "risk_level": risk_level,
        "recommendation": recommendation
    }

# Test with a sample input
sample_input = {
    "age": 52, "sex": 1, "cp": 0, "trestbps": 125, "chol": 212,
    "fbs": 0, "restecg": 1, "thalach": 168, "exang": 0, "oldpeak": 1.0,
    "slope": 2, "ca": 2, "thal": 3
}

diagnosis_result = diagnose_and_predict_heart_disease(sample_input)
print(f"Diagnosis: {diagnosis_result['diagnosis']}, Probability: {diagnosis_result['probability']:.4f}, Risk Level: {diagnosis_result['risk_level']}")
print(f"Recommendation: {diagnosis_result['recommendation']}")