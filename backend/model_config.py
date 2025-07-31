# backend/model_config.py

MODEL_URLS = {
        # Malaria Model
        "malaria_model": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/multi_class_malaria_model/multi_class_malaria_model.h5",

        # CKD Models
        "ckd_best_model_random_forest_classifier": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/ckd_model/ckd_best_model_random_forest_classifier.pkl",
        "ckd_feature_names": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/ckd_model/ckd_feature_names.pkl",
        "ckd_scaler": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/ckd_model/ckd_scaler.pkl",

        # Heart Disease Models
        "heart_disease_feature_names": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/heart_disease_model_advanced/heart_disease_feature_names.pkl",
        "heart_disease_model_advanced": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/heart_disease_model_advanced/heart_disease_model_advanced.keras", # Keras format
        "heart_disease_pca": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/heart_disease_model_advanced/heart_disease_pca.pkl",
        "heart_disease_polynomial_features": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/heart_disease_model_advanced/heart_disease_polynomial_features.pkl",
        "heart_disease_scaler": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/heart_disease_model_advanced/heart_disease_scaler.pkl",

        # Hepatitis C Models (Note: The .tf/ directory structure implies a TensorFlow SavedModel format)
        # For SavedModel format, you typically download the *entire directory* and then load from the local path.
        # Direct URL to fingerprint.pb etc. is for viewing, not direct loading by load_model().
        # We will adjust how to load these.
        "hepatitis_c_feature_names": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/hepatitis_c_model/hepatitis_c_feature_names.pkl",
        "hepatitis_c_scaler": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/hepatitis_c_model/hepatitis_c_scaler.pkl",
        "hepatitis_c_random_forest_model": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/hepatitis_c_model/random_forest_model.pkl",
        "hepatitis_c_scaler_2": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/hepatitis_c_model/scaler.pkl", # Renamed to avoid conflict
        "hepatitis_c_X_test_scaled": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/hepatitis_c_model/X_test_scaled.npy",
        "hepatitis_c_y_test": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/hepatitis_c_model/y_test.npy",
        # For 'hepatitis_c_model.tf/', you will need to handle this as a directory.
        # We'll discuss this specifically for SavedModel format loading.

        # Symptom Scan Models
        "symScan_disease_to_int_map": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/symScan/disease_to_int_map.pkl",
        "symScan_int_to_disease_map": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/symScan/int_to_disease_map.pkl",
        "symScan_precautions_map": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/symScan/precautions_map.pkl",
        "symScan_sympton_classifier_model": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/symScan/sympton_classifier_model.pkl",
        "symScan_unique_diseases": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/symScan/unique_diseases.pkl",
        "symScan_unique_symptoms": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/symScan/unique_symptoms.pkl",
    }