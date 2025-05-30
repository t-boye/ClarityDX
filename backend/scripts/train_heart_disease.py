import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
from sklearn.utils import class_weight
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, LearningRateScheduler
import numpy as np

# Paths
dataset_path = "./dataset/Heart-Disease/heart.csv"
model_save_path = "./models/heart_disease_model/heart_disease_model.h5" 

# Ensure output directory exists
os.makedirs(os.path.dirname(model_save_path), exist_ok=True)

# Load Dataset
try:
    data = pd.read_csv(dataset_path)
except FileNotFoundError:
    raise FileNotFoundError(f"❌ Dataset file not found: {dataset_path}. Check the path.")

# EDA: Check for class distribution
sns.countplot(x='target', data=data)
plt.title('Class Distribution')
plt.show()

# EDA: Check for correlations
plt.figure(figsize=(10, 8))
sns.heatmap(data.corr(), annot=True, fmt=".2f", cmap='coolwarm')
plt.title('Correlation Matrix')
plt.show()

# Data Validation
if "target" not in data.columns:
    raise ValueError("❌ The 'target' column is missing from the dataset.")

# Data Preprocessing
data = data.dropna()
X = data.drop("target", axis=1).values
y = data["target"].values

# Handle Class Imbalance
class_weights = class_weight.compute_class_weight('balanced', classes=np.unique(y), y=y)
class_weights_dict = {0: class_weights[0], 1: class_weights[1]}

# Split Data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale Features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Convert to float32 for TensorFlow compatibility
X_train_scaled = X_train_scaled.astype(np.float32)
y_train = y_train.astype(np.float32)
X_test_scaled = X_test_scaled.astype(np.float32)
y_test = y_test.astype(np.float32)

# Define Learning Rate Scheduler
def lr_scheduler(epoch, lr):
    if epoch > 20:
        return lr * 0.5  # Reduce learning rate after 20 epochs
    return lr

# Build Model
def create_model():
    model = Sequential([
        Dense(256, activation='relu', input_shape=(X_train_scaled.shape[1],)),
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
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

# Initialize and Train Model
model = create_model()
early_stopping = EarlyStopping(monitor="val_loss", patience=10, restore_best_weights=True)
lr_callback = LearningRateScheduler(lr_scheduler)

history = model.fit(
    X_train_scaled, y_train,
    validation_split=0.2,
    epochs=100,
    batch_size=32,
    class_weight=class_weights_dict,  # Use class weights
    callbacks=[early_stopping, lr_callback],
    verbose=1
)

# Evaluate Model
y_pred = (model.predict(X_test_scaled) > 0.5).astype(int)
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)

print(f"✅ Test Accuracy: {accuracy}")
print("📄 Classification Report:")
print(report)

# Save Model in TensorFlow's SavedModel format
model.save(model_save_path)
print(f"✅ Model saved to {model_save_path}")

# Optional: Visualize training history
plt.figure(figsize=(12, 4))
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Train Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.title('Model Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Model Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()

plt.tight_layout()
plt.show()