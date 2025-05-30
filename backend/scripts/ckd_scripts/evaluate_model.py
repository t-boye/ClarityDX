import pandas as pd
import joblib
import os
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_curve, auc
import seaborn as sns
import matplotlib.pyplot as plt

# Load the model and scaler
model_path = r"C:\Users\USER\Documents\GitHub\malaria-expert-system\backend\models\ckd_model\ckd_model.pkl"
scaler_path = r"C:\Users\USER\Documents\GitHub\malaria-expert-system\backend\models\ckd_model\ckd_scaler.pkl"

model = joblib.load(model_path)
scaler = joblib.load(scaler_path)

# Load dataset for evaluation
data_path = r"C:\Users\USER\Documents\GitHub\malaria-expert-system\backend\dataset\CKD\CKD_Preprocessed.csv"  # Adjust path if needed
df = pd.read_csv(data_path)

# Display basic information about the dataset
print("Dataset Information:")
print(df.info())
print("\nFirst few rows of the dataset:")
print(df.head())

# Identify the target column dynamically
possible_targets = [col for col in df.columns if "disease" in col.lower() or "class" in col.lower()]
if not possible_targets:
    raise ValueError("No valid target column found in dataset.")
target_col = possible_targets[0]  # Use the first match

# Separate features (X) and target (y)
X = df.drop(columns=[target_col])
y = df[target_col]

# Check for missing values
if df.isnull().sum().sum() > 0:
    print("Warning: Dataset contains missing values. Consider handling them.")
else:
    print("No missing values found in the dataset.")

# Display class distribution
print("\nClass distribution:")
print(y.value_counts())

# Standardize features using the loaded scaler
X_scaled = scaler.transform(X)

# Make predictions
y_pred = model.predict(X_scaled)

# Evaluate model
accuracy = accuracy_score(y, y_pred)
print(f"\nModel Accuracy: {accuracy:.4f}")

# Display classification report
print("\nClassification Report:")
print(classification_report(y, y_pred))

# Plot confusion matrix
cm = confusion_matrix(y, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=possible_targets, yticklabels=possible_targets)
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.title('Confusion Matrix')
plt.show()

# Plot ROC curve (for binary classification)
y_prob = model.predict_proba(X_scaled)[:, 1]  # Get probabilities for the positive class
fpr, tpr, thresholds = roc_curve(y, y_prob)
roc_auc = auc(fpr, tpr)

plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='blue', label='ROC curve (area = %0.2f)' % roc_auc)
plt.plot([0, 1], [0, 1], color='red', linestyle='--')  # Diagonal line
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic')
plt.legend(loc="lower right")
plt.show()

# Plot feature importance
feature_names = X.columns
coefficients = model.coef_[0]
importance_df = pd.DataFrame({'Feature': feature_names, 'Coefficient': coefficients})
importance_df = importance_df.sort_values(by='Coefficient', ascending=False)

plt.figure(figsize=(10, 6))
sns.barplot(x='Coefficient', y='Feature', data=importance_df)
plt.title('Feature Importance')
plt.show()