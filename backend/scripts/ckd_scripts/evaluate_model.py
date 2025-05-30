import pandas as pd
import joblib
import os
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_curve, auc
import seaborn as sns
import matplotlib.pyplot as plt

# Get current directory and construct paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..', '..'))
MODELS_DIR = os.path.join(BACKEND_DIR, 'models')
DATASET_DIR = os.path.join(BACKEND_DIR, 'dataset')

# Load the model and scaler
try:
    model = joblib.load(os.path.join(MODELS_DIR, "ckd_model", "ckd_model.pkl"))
    scaler = joblib.load(os.path.join(MODELS_DIR, "ckd_model", "ckd_scaler.pkl"))
except Exception as e:
    raise FileNotFoundError(f"Failed to load model artifacts: {str(e)}")

# Load dataset for evaluation
try:
    df = pd.read_csv(os.path.join(DATASET_DIR, "CKD", "CKD_Preprocessed.csv"))
except Exception as e:
    raise FileNotFoundError(f"Failed to load dataset: {str(e)}")

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
try:
    X_scaled = scaler.transform(X)
except Exception as e:
    raise ValueError(f"Feature scaling failed: {str(e)}")

# Make predictions
try:
    y_pred = model.predict(X_scaled)
except Exception as e:
    raise ValueError(f"Prediction failed: {str(e)}")

# Evaluate model
accuracy = accuracy_score(y, y_pred)
print(f"\nModel Accuracy: {accuracy:.4f}")

# Display classification report
print("\nClassification Report:")
print(classification_report(y, y_pred))

# Plot confusion matrix
plt.figure(figsize=(8, 6))
cm = confusion_matrix(y, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['Negative', 'Positive'], 
            yticklabels=['Negative', 'Positive'])
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.title('Confusion Matrix')
plt.tight_layout()
plt.savefig('confusion_matrix.png')
plt.close()

# Plot ROC curve (for binary classification)
if hasattr(model, "predict_proba"):
    try:
        y_prob = model.predict_proba(X_scaled)[:, 1]
        fpr, tpr, thresholds = roc_curve(y, y_prob)
        roc_auc = auc(fpr, tpr)

        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='blue', label=f'ROC curve (area = {roc_auc:.2f})')
        plt.plot([0, 1], [0, 1], color='red', linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver Operating Characteristic')
        plt.legend(loc="lower right")
        plt.tight_layout()
        plt.savefig('roc_curve.png')
        plt.close()
    except Exception as e:
        print(f"Could not generate ROC curve: {str(e)}")

# Plot feature importance (if model supports it)
if hasattr(model, "coef_"):
    try:
        feature_names = X.columns
        coefficients = model.coef_[0]
        importance_df = pd.DataFrame({'Feature': feature_names, 'Coefficient': coefficients})
        importance_df = importance_df.sort_values(by='Coefficient', ascending=False)

        plt.figure(figsize=(10, 6))
        sns.barplot(x='Coefficient', y='Feature', data=importance_df)
        plt.title('Feature Importance')
        plt.tight_layout()
        plt.savefig('feature_importance.png')
        plt.close()
    except Exception as e:
        print(f"Could not generate feature importance plot: {str(e)}")

print("\nAll operations completed successfully. Plots saved to current directory.")