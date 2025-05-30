import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.impute import SimpleImputer # Import SimpleImputer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def train_and_evaluate_ckd_model(data_path, model_dir):
    """
    Trains and evaluates a Logistic Regression model for Chronic Kidney Disease (CKD) prediction.

    Args:
        data_path (str): Path to the CSV dataset.
        model_dir (str): Path to the directory for saving model artifacts.
    """
    try:
        # Load dataset
        df = pd.read_csv(data_path)
        logging.info(f"Dataset loaded from {data_path}")

        # Display basic information about the dataset
        logging.info("Dataset Information:")
        logging.info(df.info())
        logging.info("\nFirst few rows of the dataset:")
        logging.info(df.head())

        # Explicitly specify the target column
        target_col = "Chronic Kidney Disease: yes"  # Corrected target column name

        # Separate features (X) and target (y)
        X = df.drop(columns=[target_col])
        y = df[target_col]

        # Handle missing values using imputation
        imputer = SimpleImputer(strategy='median')  # Choose an appropriate strategy
        X = pd.DataFrame(imputer.fit_transform(X), columns=X.columns) # Convert back to dataframe

        logging.info("Missing values handled using imputation.")


        # Display class distribution
        logging.info("\nClass distribution:")
        logging.info(y.value_counts())

        # Split data into training and testing sets (80% train, 20% test)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        logging.info("Data split into training and testing sets.")

        # Standardize features
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)
        logging.info("Features scaled using StandardScaler.")

        # Define parameter grid for GridSearchCV
        param_grid = {
            'C': [0.01, 0.1, 1, 10, 100],
            'solver': ['liblinear', 'saga'],
            'class_weight': ['balanced']  # Keep class_weight balanced
        }

        # Train Logistic Regression model with GridSearchCV for hyperparameter tuning
        model = LogisticRegression(max_iter=1000, random_state=42)
        grid_search = GridSearchCV(model, param_grid, cv=5, scoring='accuracy', verbose=1)  # Use GridSearchCV
        grid_search.fit(X_train, y_train)

        logging.info("Best parameters found by GridSearchCV:")
        logging.info(grid_search.best_params_)
        best_model = grid_search.best_estimator_ #get the best model.

        logging.info("Logistic Regression model trained using GridSearchCV.")

        # Evaluate model
        y_pred = best_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        logging.info(f"\nModel Accuracy: {accuracy:.4f}")

        # Display classification report
        logging.info("\nClassification Report:")
        logging.info(classification_report(y_test, y_pred))

        # Display confusion matrix
        logging.info("\nConfusion Matrix:")
        logging.info(confusion_matrix(y_test, y_pred))

        # Create model directory if it doesn't exist
        os.makedirs(model_dir, exist_ok=True)

        # Define model save paths
        model_path = os.path.join(model_dir, "ckd_model.pkl")
        scaler_path = os.path.join(model_dir, "ckd_scaler.pkl")
        feature_names_path = os.path.join(model_dir, "ckd_feature_names.pkl")

        # Save model, scaler, and feature names
        joblib.dump(best_model, model_path) #save the best model
        joblib.dump(scaler, scaler_path)
        joblib.dump(X.columns.tolist(), feature_names_path)
        logging.info(f"\nModel saved to {model_path}")
        logging.info(f"Scaler saved to {scaler_path}")
        logging.info(f"Feature names saved to {feature_names_path}")

        # Print feature names
        logging.info("Feature columns used for training:")
        logging.info(X.columns.tolist())

        return best_model, scaler, X.columns.tolist() # return the model, scaler and feature names.

    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
        raise  # Re-raise the exception to stop execution

if __name__ == "__main__":
    # Specify data path and model directory
    data_path = r"C:\Users\USER\Documents\GitHub\malaria-expert-system\backend\dataset\CKD\CKD_Preprocessed.csv"
    model_dir = r"C:\Users\USER\Documents\GitHub\malaria-expert-system\backend\models\ckd_model"
    # Train and evaluate the model
    trained_model, scaler, feature_names = train_and_evaluate_ckd_model(data_path, model_dir)
