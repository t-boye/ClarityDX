import joblib
import os
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def display_ckd_model_results(model_dir, model_name):
    """
    Loads and displays the classification report and confusion matrix for a specific CKD model.

    Args:
        model_dir (str): Path to the directory where model artifacts are saved.
        model_name (str): The name of the model to display results for (e.g., 'Ensemble Voting Classifier').
    """
    results_path = os.path.join(model_dir, "ckd_all_model_results.pkl")
    
    try:
        all_model_results = joblib.load(results_path)
        logging.info(f"Loaded all model results from {results_path}")
        
        if model_name in all_model_results:
            model_data = all_model_results[model_name]
            
            logging.info(f"\n--- Detailed Results for {model_name} ---")
            logging.info(f"Accuracy: {model_data['accuracy']:.4f}")
            
            # Print Classification Report
            report_dict = model_data['classification_report']
            
            # Extract metrics for positive class (assuming '1' or 1.0 or '1.0' as key)
            positive_class_metrics = None
            if '1' in report_dict:
                positive_class_metrics = report_dict['1']
            elif 1.0 in report_dict:
                positive_class_metrics = report_dict[1.0]
            elif '1.0' in report_dict:
                positive_class_metrics = report_dict['1.0']

            if positive_class_metrics:
                logging.info(f"Precision (Class 1): {positive_class_metrics['precision']:.4f}")
                logging.info(f"Recall (Class 1): {positive_class_metrics['recall']:.4f}")
                logging.info(f"F1-Score (Class 1): {positive_class_metrics['f1-score']:.4f}")
            else:
                logging.warning("Could not find positive class metrics in classification report.")
            
            logging.info(f"\nFull Classification Report:\n{pd.DataFrame(report_dict).transpose()}")


            # Print Confusion Matrix
            cm = model_data['confusion_matrix']
            # Assuming cm is a list of lists, convert to DataFrame for pretty print
            cm_df = pd.DataFrame(cm, index=['Actual Positive', 'Actual Negative'], columns=['Predicted Positive', 'Predicted Negative'])
            logging.info(f"\nConfusion Matrix:\n{cm_df}")
            
        else:
            logging.warning(f"Model '{model_name}' not found in the saved results.")
            logging.info(f"Available models: {list(all_model_results.keys())}")
            
    except FileNotFoundError:
        logging.error(f"Error: Results file not found at {results_path}.")
        logging.error("Please ensure you have run 'train_ckd_model.py' after modifying it to save 'ckd_all_model_results.pkl'.")
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    # Ensure this path matches where your models are saved
    model_dir = r"C:\Users\USER\Documents\GitHub\Multi-Disease-Diagnosis-System-v0\backend\models\ckd_model\ckd_best_model_random_forest_classifier.pkl" 

    # Display results for the Ensemble Voting Classifier
    display_ckd_model_results(model_dir, 'Ensemble Voting Classifier')
    
    # You can also display results for other models for comparison
    display_ckd_model_results(model_dir, 'Random Forest Classifier')
    display_ckd_model_results(model_dir, 'Decision Tree Classifier')