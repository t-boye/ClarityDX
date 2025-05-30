# C:\Users\USER\Documents\GitHub\malaria-expert-system\backend\scripts\train_cancer_model.py

import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
from cancer_scripts.cancer_data_preprocessing import preprocess_data  # Import preprocessing
import os #to make directories

# Define the data path
DATA_PATH = r"C:\Users\USER\Documents\GitHub\malaria-expert-system\backend\dataset\Cancer Prediction\The_Cancer_data_1500_V2.csv"

# Define the model save directory
MODEL_DIR = r"C:\Users\USER\Documents\GitHub\malaria-expert-system\backend\models\cancer_model"

# Create the directory if it doesn't exist
os.makedirs(MODEL_DIR, exist_ok=True)

# Preprocess the data
X_train_scaled, X_test_scaled, y_train, y_test = preprocess_data(DATA_PATH)

if X_train_scaled is not None:  # Check if preprocessing was successful
    # Choose and train a model (Logistic Regression example)
    model_logreg = LogisticRegression(random_state=42)
    model_logreg.fit(X_train_scaled, y_train)

    # Make predictions
    y_pred_logreg = model_logreg.predict(X_test_scaled)

    # Evaluate the model
    accuracy_logreg = accuracy_score(y_test, y_pred_logreg)
    report_logreg = classification_report(y_test, y_pred_logreg)
    auc_logreg = roc_auc_score(y_test, model_logreg.predict_proba(X_test_scaled)[:, 1])

    print("Logistic Regression Results:")
    print("Accuracy:", accuracy_logreg)
    print("Classification Report:\n", report_logreg)
    print("AUC-ROC:", auc_logreg)

    # Save the trained model to the specified directory
    joblib.dump(model_logreg, os.path.join(MODEL_DIR, 'cancer_logreg_model.joblib'))

    # Choose and train a model (Random Forest example)
    model_rf = RandomForestClassifier(random_state=42)
    model_rf.fit(X_train_scaled, y_train)

    # Make predictions
    y_pred_rf = model_rf.predict(X_test_scaled)

    # Evaluate the model
    accuracy_rf = accuracy_score(y_test, y_pred_rf)
    report_rf = classification_report(y_test, y_pred_rf)
    auc_rf = roc_auc_score(y_test, model_rf.predict_proba(X_test_scaled)[:, 1])

    print("\nRandom Forest Results:")
    print("Accuracy:", accuracy_rf)
    print("Classification Report:\n", report_rf)
    print("AUC-ROC:", auc_rf)

    # Save the trained model to the specified directory
    joblib.dump(model_rf, os.path.join(MODEL_DIR, 'cancer_rf_model.joblib'))

else:
    print("Preprocessing failed. Model training aborted.")