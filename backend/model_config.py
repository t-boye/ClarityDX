# Model URLs configuration

MODEL_URLS = {
    # Malaria Model
    "malaria_model": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/multi_class_malaria_model/multi_class_malaria_model.h5",

    # CKD Models
    "ckd_model": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/ckd_model/ckd_best_model_random_forest_classifier.pkl",
    "ckd_feature_names": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/ckd_model/ckd_feature_names.pkl",
    "ckd_scaler": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/ckd_model/ckd_scaler.pkl",

    # Heart Disease Models
    "heart_disease_model": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/heart_disease_model_advanced/heart_disease_model_advanced.keras",
    "heart_disease_scaler": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/heart_disease_model_advanced/heart_disease_scaler.pkl",
    "heart_disease_pca": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/heart_disease_model_advanced/heart_disease_pca.pkl",
    "heart_disease_polynomial_features": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/heart_disease_model_advanced/heart_disease_polynomial_features.pkl",
    "heart_disease_feature_names": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/heart_disease_model_advanced/heart_disease_feature_names.pkl",

    # Hepatitis C Models
    "hepatitis_c_model": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/hepatitis_c_model/random_forest_model.pkl",
    "hepatitis_c_scaler": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/hepatitis_c_model/hepatitis_c_scaler.pkl",
    "hepatitis_c_feature_names": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/hepatitis_c_model/hepatitis_c_feature_names.pkl",

    # SymScan Models
    "symScan_sympton_classifier_model": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/symScan/sympton_classifier_model.pkl",
    "symScan_int_to_disease_map": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/symScan/int_to_disease_map.pkl",
    "symScan_precautions_map": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/symScan/precautions_map.pkl",
    "symScan_unique_symptoms": "https://claritydx-ai-models-2025.s3.us-east-1.amazonaws.com/symScan/unique_symptoms.pkl",
}
