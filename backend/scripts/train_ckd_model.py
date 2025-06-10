import pandas as pd
import joblib
import os
import matplotlib
matplotlib.use('Agg') # Set Matplotlib backend BEFORE importing pyplot
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import logging

# Import models
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_curve, auc

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def save_confusion_matrix(conf_matrix, model_name, img_dir):
    """Save the confusion matrix as an image."""
    plt.figure(figsize=(8, 6))
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', cbar=False,
                xticklabels=['No CKD', 'CKD'], yticklabels=['No CKD', 'CKD'])
    plt.title(f'Confusion Matrix for {model_name}')
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, f'{model_name.replace(" ", "_").lower()}_confusion_matrix.png'))
    plt.close()
    logging.info(f"Saved {model_name} confusion matrix to {img_dir}")

def save_classification_report(report, model_name, img_dir):
    """Save the classification report as a bar chart image."""
    if '1' in report:
        positive_class_metrics = report['1']
    elif 1.0 in report:
        positive_class_metrics = report[1.0]
    elif '1.0' in report:
        positive_class_metrics = report['1.0']
    else:
        logging.warning(f"Positive class (1 or 1.0) not found in classification report keys for {model_name}. Skipping classification report plot.")
        return

    metrics_to_plot = {k: v for k, v in positive_class_metrics.items() if k not in ['support']}
    plt.figure(figsize=(8, 6))
    plt.title(f"{model_name} Classification Report (Class 1)")
    plt.bar(list(metrics_to_plot.keys()), list(metrics_to_plot.values()), color='skyblue', alpha=0.8)
    plt.ylim(0, 1.0)
    plt.ylabel('Score')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, f'{model_name.replace(" ", "_").lower()}_classification_report_class_1.png'))
    plt.close()
    logging.info(f"Saved {model_name} classification report for class 1 to {img_dir}")

def save_roc_curve(model, X_test_scaled, y_test, model_name, img_dir):
    """Save the ROC curve as an image."""
    if hasattr(model, "predict_proba"):
        y_proba = model.predict_proba(X_test_scaled)[:, 1]
        fpr, tpr, _ = roc_curve(y_test, y_proba)
        roc_auc = auc(fpr, tpr)

        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(f'ROC Curve for {model_name}')
        plt.legend(loc="lower right")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(img_dir, f'{model_name.replace(" ", "_").lower()}_roc_curve.png'))
        plt.close()
        logging.info(f"Saved {model_name} ROC curve to {img_dir}")
    else:
        logging.warning(f"{model_name} does not support predict_proba, skipping ROC curve plot.")

def train_and_evaluate_models(X_train_scaled, y_train, X_test_scaled, y_test, img_dir):
    """Train and evaluate multiple models, returning their results."""
    all_model_results = {}
    best_overall_accuracy = 0
    best_overall_model_name = None
    best_overall_model = None

    models_to_train = {
        'Logistic Regression': {
            'model': LogisticRegression(max_iter=1000, random_state=42),
            'param_grid': {
                'C': [0.01, 0.1, 1, 10, 100],
                'solver': ['liblinear', 'saga'],
                'class_weight': ['balanced']
            }
        },
        'Random Forest Classifier': {
            'model': RandomForestClassifier(random_state=42),
            'param_grid': {
                'n_estimators': [50, 100, 200],
                'max_depth': [None, 10, 20],
                'min_samples_split': [2, 5],
                'class_weight': ['balanced']
            }
        },
        'K-Nearest Neighbors Classifier': {
            'model': KNeighborsClassifier(),
            'param_grid': {
                'n_neighbors': [3, 5, 7, 9],
                'weights': ['uniform', 'distance'],
                'metric': ['euclidean', 'manhattan']
            }
        },
        'Decision Tree Classifier': {
            'model': DecisionTreeClassifier(random_state=42),
            'param_grid': {
                'max_depth': [None, 5, 10, 20],
                'min_samples_split': [2, 5, 10],
                'class_weight': ['balanced']
            }
        }
    }

    for model_name, model_info in models_to_train.items():
        logging.info(f"\n--- Training and evaluating {model_name} ---")
        model = model_info['model']
        param_grid = model_info['param_grid']

        grid_search = GridSearchCV(model, param_grid, cv=5, scoring='accuracy', verbose=1, n_jobs=-1)
        grid_search.fit(X_train_scaled, y_train)

        logging.info(f"Best parameters for {model_name}: {grid_search.best_params_}")
        best_model_for_algo = grid_search.best_estimator_

        y_pred = best_model_for_algo.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True)
        conf_matrix = confusion_matrix(y_test, y_pred)

        # Extract precision, recall, and F1-score for the positive class
        precision = report['1']['precision'] if '1' in report else report[1.0]['precision']
        recall = report['1']['recall'] if '1' in report else report[1.0]['recall']
        f1_score = report['1']['f1-score'] if '1' in report else report[1.0]['f1-score']

        logging.info(f"{model_name} Accuracy: {accuracy:.4f}")
        logging.info(f"{model_name} Precision: {precision:.4f}")
        logging.info(f"{model_name} Recall: {recall:.4f}")
        logging.info(f"{model_name} F1-Score: {f1_score:.4f}")
        logging.info(f"{model_name} Classification Report:\n{classification_report(y_test, y_pred)}")
        logging.info(f"{model_name} Confusion Matrix:\n{conf_matrix}")

        all_model_results[model_name] = {
            'best_params': grid_search.best_params_,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'classification_report': report,
            'confusion_matrix': conf_matrix.tolist(),
            'model_object': best_model_for_algo
        }

        if accuracy > best_overall_accuracy:
            best_overall_accuracy = accuracy
            best_overall_model_name = model_name
            best_overall_model = best_model_for_algo

        save_confusion_matrix(conf_matrix, model_name, img_dir)
        save_classification_report(report, model_name, img_dir)
        save_roc_curve(best_model_for_algo, X_test_scaled, y_test, model_name, img_dir)

    # --- Add Ensemble Voting Classifier training and evaluation ---
    logging.info("\n--- Training and evaluating Ensemble Voting Classifier ---")

    # Ensure all base models have been trained and are available in all_model_results
    # It's good practice to ensure they support predict_proba for 'soft' voting
    estimators = []
    if 'Random Forest Classifier' in all_model_results:
        estimators.append(('rf', all_model_results['Random Forest Classifier']['model_object']))
    if 'K-Nearest Neighbors Classifier' in all_model_results:
        # KNN supports predict_proba by default
        estimators.append(('knn', all_model_results['K-Nearest Neighbors Classifier']['model_object']))
    if 'Decision Tree Classifier' in all_model_results:
        estimators.append(('dt', all_model_results['Decision Tree Classifier']['model_object']))
    if 'Logistic Regression' in all_model_results:
        estimators.append(('lr', all_model_results['Logistic Regression']['model_object']))


    if estimators:
        # Using 'soft' voting requires all estimators to have predict_proba method
        # LogisticRegression, RandomForestClassifier, DecisionTreeClassifier, KNeighborsClassifier
        # all support predict_proba.
        voting_clf = VotingClassifier(estimators=estimators, voting='soft', n_jobs=-1)
        voting_clf.fit(X_train_scaled, y_train)

        y_pred_voting = voting_clf.predict(X_test_scaled)
        accuracy_voting = accuracy_score(y_test, y_pred_voting)
        report_voting = classification_report(y_test, y_pred_voting, output_dict=True)
        conf_matrix_voting = confusion_matrix(y_test, y_pred_voting)

        precision_voting = report_voting['1']['precision'] if '1' in report_voting else report_voting[1.0]['precision']
        recall_voting = report_voting['1']['recall'] if '1' in report_voting else report_voting[1.0]['recall']
        f1_score_voting = report_voting['1']['f1-score'] if '1' in report_voting else report_voting[1.0]['f1-score']

        logging.info(f"Ensemble Voting Classifier Accuracy: {accuracy_voting:.4f}")
        logging.info(f"Ensemble Voting Classifier Precision: {precision_voting:.4f}")
        logging.info(f"Ensemble Voting Classifier Recall: {recall_voting:.4f}")
        logging.info(f"Ensemble Voting Classifier F1-Score: {f1_score_voting:.4f}")
        logging.info(f"Ensemble Voting Classifier Classification Report:\n{classification_report(y_test, y_pred_voting)}")
        logging.info(f"Ensemble Voting Classifier Confusion Matrix:\n{conf_matrix_voting}")

        all_model_results['Ensemble Voting Classifier'] = {
            'best_params': {}, # VotingClassifier typically doesn't have 'best_params' in the same way
            'accuracy': accuracy_voting,
            'precision': precision_voting,
            'recall': recall_voting,
            'f1_score': f1_score_voting,
            'classification_report': report_voting,
            'confusion_matrix': conf_matrix_voting.tolist(),
            'model_object': voting_clf
        }

        if accuracy_voting > best_overall_accuracy:
            best_overall_accuracy = accuracy_voting
            best_overall_model_name = 'Ensemble Voting Classifier'
            best_overall_model = voting_clf

        save_confusion_matrix(conf_matrix_voting, 'Ensemble Voting Classifier', img_dir)
        save_classification_report(report_voting, 'Ensemble Voting Classifier', img_dir)
        save_roc_curve(voting_clf, X_test_scaled, y_test, 'Ensemble Voting Classifier', img_dir)
    else:
        logging.warning("Skipping Ensemble Voting Classifier as no base estimators were available.")
    # --- End of Ensemble Voting Classifier section ---


    return all_model_results, best_overall_model_name, best_overall_model, best_overall_accuracy

def main(data_path, model_dir, img_dir):
    """Main function to execute the training and evaluation process."""
    # Load dataset
    df = pd.read_csv(data_path)
    logging.info(f"Dataset loaded from {data_path}")

    # Explicitly specify the target column
    target_col = "Chronic Kidney Disease: yes"

    # Log unique values before cleaning
    logging.info(f"Unique values in target column before cleaning: {df[target_col].unique()}")

    # Strip whitespace and convert to lowercase
    # This also converts initial float values (e.g., 1.0) to string '1.0'
    df[target_col] = df[target_col].astype(str).str.strip().str.lower()

    # Replace problematic string representations with NaN
    df[target_col] = df[target_col].replace({
        '?': pd.NA,
        '': pd.NA,
        ' ': pd.NA,
        'nan': pd.NA, # This catches the string 'nan' if float NaNs were converted
        'n/a': pd.NA,
        '-': pd.NA
    })

    # Log unique values after initial replacement (before dropping NaNs)
    logging.info(f"Unique values in target column after replacement: {df[target_col].unique()}")

    # Drop rows with NaN values in the target column
    initial_rows = len(df)
    df.dropna(subset=[target_col], inplace=True)
    rows_after_dropna = len(df)
    if initial_rows > rows_after_dropna:
        logging.info(f"Dropped {initial_rows - rows_after_dropna} rows due to NaN values in the target column.")

    # Convert remaining valid string representations ('yes', 'no', '1.0', '0.0') to numerical
    df[target_col] = df[target_col].replace({'yes': 1, 'no': 0, '1.0': 1, '0.0': 0}).astype(int)
    # The .astype(int) explicitly converts to integer, handling the FutureWarning

    # Log unique values after final mapping and type conversion
    logging.info(f"Unique values in target column after mapping: {df[target_col].unique()}")

    # Final check for NaN values (should not be any at this point if cleaning was successful)
    if df[target_col].isnull().any():
        logging.error("Target column still contains NaN values after cleaning. Unique values remaining: %s", df[target_col].unique())
        raise ValueError("Target column still contains NaN values.")

    # Separate features (X) and target (y)
    X = df.drop(columns=[target_col])
    y = df[target_col]

    # Handle missing values in features using imputation
    imputer = SimpleImputer(strategy='median')
    # Ensure X is a DataFrame before imputation to preserve column names
    X = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)
    logging.info("Missing values handled using imputation.")

    # Log unique values in the target variable
    logging.info(f"Unique values in target variable: {y.unique()}")

    # Split data into training and testing sets (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    logging.info("Data split into training and testing sets.")

    # Standardize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    logging.info("Features scaled using StandardScaler.")

    # Create directories if they don't exist
    os.makedirs(model_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)
    logging.info(f"Model directory created at {model_dir}")
    logging.info(f"Image directory created at {img_dir}")

    # Train and evaluate models
    all_model_results, best_overall_model_name, best_overall_model, best_overall_accuracy = train_and_evaluate_models(X_train_scaled, y_train, X_test_scaled, y_test, img_dir)

    logging.info(f"\n--- Best overall model: {best_overall_model_name} with Accuracy: {best_overall_accuracy:.4f} ---")

    # Save the best overall model
    if best_overall_model:
        model_path = os.path.join(model_dir, f"ckd_best_model_{best_overall_model_name.replace(' ', '_').lower()}.pkl")
        joblib.dump(best_overall_model, model_path)
        logging.info(f"Best overall model ({best_overall_model_name}) saved to {model_path}")

    # Save scaler and feature names
    scaler_path = os.path.join(model_dir, "ckd_scaler.pkl")
    feature_names_path = os.path.join(model_dir, "ckd_feature_names.pkl")
    joblib.dump(scaler, scaler_path)
    joblib.dump(X.columns.tolist(), feature_names_path)
    logging.info(f"Scaler saved to {scaler_path}")
    logging.info(f"Feature names saved to {feature_names_path}")

    # Print feature names
    logging.info("Feature columns used for training:")
    logging.info(X.columns.tolist())


if __name__ == "__main__":
    # Specify data path, model directory, and image directory
    data_path = r"C:\Users\USER\Documents\GitHub\Multi-Disease-Diagnosis-System-v0\backend\dataset\CKD\CKD_Preprocessed.csv"
    model_dir = r"C:\Users\USER\Documents\GitHub\Multi-Disease-Diagnosis-System-v0\backend\models\ckd_model"
    img_dir = r"C:\Users\USER\Documents\GitHub\Multi-Disease-Diagnosis-System-v0\backend\scripts\ckd_scripts\img"

    # Train and evaluate all models
    main(data_path, model_dir, img_dir)