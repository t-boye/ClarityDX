import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report

# Paths
model_path = r"C:/Users/USER/Documents/GitHub/malaria-expert-system/backend/models/hepatitis_c_model/hepatitis_c_model_balanced.h5"

test_data_path = r"C:/Users/USER/Documents/GitHub/malaria-expert-system/backend/dataset/HepatitisCdata/HepatitisCdata.csv"

# 1. Load Test Data
try:
    data = pd.read_csv(test_data_path)
except FileNotFoundError:
    raise FileNotFoundError(f"\u274c Test dataset not found: {test_data_path}. Check the path.")

# 2. Preprocess Data
# Identify categorical columns and encode them
categorical_columns = ["Sex"]  # Add other categorical columns if needed
encoder = LabelEncoder()
for col in categorical_columns:
    data[col] = encoder.fit_transform(data[col])

# Drop rows with missing values
data = data.dropna()

# Ensure the 'Category' column exists for testing
if "Category" not in data.columns:
    raise ValueError("\u274c The 'Category' column is missing from the test dataset.")

# Split features and labels
X_test = data.drop("Category", axis=1).values
y_test = data["Category"].values

# Standardize features
scaler = StandardScaler()
X_test_scaled = scaler.fit_transform(X_test)
X_test_scaled = X_test_scaled.astype(np.float32)

# Encode labels
label_encoder = LabelEncoder()
y_test_encoded = label_encoder.fit_transform(y_test)

# 3. Load Model
try:
    model = tf.keras.models.load_model(model_path)
except Exception as e:
    raise ValueError(f"\u274c Failed to load model: {e}")

# 4. Make Predictions
y_pred_probs = model.predict(X_test_scaled)
y_pred = np.argmax(y_pred_probs, axis=1)  # For multi-class classification

# 5. Evaluate Model
accuracy = accuracy_score(y_test_encoded, y_pred)
report = classification_report(y_test_encoded, y_pred, target_names=label_encoder.classes_)

print(f"\u2705 Test Accuracy: {accuracy}")
print("\ud83d\udcc4 Classification Report:")
print("📄Classification Report:")
