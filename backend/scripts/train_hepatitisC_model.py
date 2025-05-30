import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, RobustScaler
from sklearn.utils.class_weight import compute_class_weight
from imblearn.over_sampling import SMOTE
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, f1_score
from sklearn.exceptions import UndefinedMetricWarning
import warnings
import os

# Suppress warnings
warnings.filterwarnings("ignore", category=UndefinedMetricWarning)

# Paths
DATA_PATH = r"C:/Users/USER/Documents/GitHub/malaria-expert-system/backend/dataset/HepatitisCdata/HepatitisCdata.csv"
MODEL_SAVE_PATH = r"C:/Users/USER/Documents/GitHub/malaria-expert-system/backend/models/hepatitis_c_model/hepatitis_c_model.keras"

def load_and_preprocess_data(data_path):
    """Loads dataset, handles missing values, encodes categorical variables,
    performs feature engineering, and removes outliers."""
    df = pd.read_csv(data_path)

    # Drop the `Unnamed: 0` column
    df.drop(columns=['Unnamed: 0'], inplace=True)

    # Clean the `Category` column
    df['Category'] = df['Category'].str.split('=').str[0].str.replace('s', '', regex=False)
    df['Category'] = pd.to_numeric(df['Category'], errors='coerce')

    # Encode the `Sex` column
    df['Sex'] = df['Sex'].map({'m': 0, 'f': 1}) # Use map

    # Impute missing values for specific columns
    for col in ['ALB', 'ALP', 'ALT', 'CHOL', 'PROT']:
        df[col] = df[col].fillna(df[col].median())  # Avoid inplace warning

    # Feature Engineering: AST/ALT ratio
    df['AST/ALT'] = df['AST'] / (df['ALT'] + 1e-7)

    # Feature Engineering: Age Groups
    df['AgeGroup_Middle'] = ((df['Age'] >= 30) & (df['Age'] <= 50)).astype(int)
    df['AgeGroup_Old'] = (df['Age'] > 50).astype(int)


    # Remove outliers using IQR method
    for col in df.select_dtypes(include=np.number).columns:
        if col not in ['Category', 'Sex', 'AgeGroup_Middle', 'AgeGroup_Old']: # exclude new cols
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]

    # Prepare features and target variable
    X = df.drop(columns=["Category"]).values
    y = df["Category"].values
    feature_names = df.drop(columns=["Category"]).columns.tolist()
    return X, y, feature_names

def balance_data(X, y):
    """Handles class imbalance using SMOTE."""
    print("🔍 Original class distribution:\n", pd.Series(y).value_counts())

    # Check for classes with fewer than 2 samples (Reduced threshold)
    class_counts = pd.Series(y).value_counts()
    classes_to_remove = class_counts[class_counts < 2].index.tolist() # Changed threshold to 2

    if classes_to_remove:
        print(f"⚠️ Classes with fewer than 2 samples: {classes_to_remove}")
        # Remove these classes from the dataset
        indices_to_keep = ~np.isin(y, classes_to_remove)
        X = X[indices_to_keep]
        y = y[indices_to_keep]
        print("✅ New class distribution after removing samples:\n", pd.Series(y).value_counts())

    # Check if we have more than one class left
    if len(np.unique(y)) < 2:
        print("⚠️  Insufficient number of classes (less than 2) for SMOTE. Skipping SMOTE.")
        return X, y  # Return the original data without resampling

    # Determine the number of neighbors for SMOTE.  Use a maximum of 3.
    n_neighbors = min(np.min(pd.Series(y).value_counts()) - 1, 3) # changed from 5 to 3 and added min
    print(f"Number of neighbors for SMOTE: {n_neighbors}")
    # Apply SMOTE
    smote = SMOTE(sampling_strategy='auto', random_state=42, k_neighbors=n_neighbors)
    X_resampled, y_resampled = smote.fit_resample(X, y)

    print("✅ Balanced class distribution:\n", pd.Series(y_resampled).value_counts())
    return X_resampled, y_resampled

def prepare_data(X, y):
    """Splits data and scales features."""
    # Check class distribution before splitting
    class_counts = pd.Series(y).value_counts()
    classes_to_remove = class_counts[class_counts < 2].index.tolist()  # Classes with < 2 samples

    if classes_to_remove:
        print(f"Removing {len(classes_to_remove)} classes with fewer than 2 samples: {classes_to_remove}")
        indices_to_keep = ~np.isin(y, classes_to_remove)
        X = X[indices_to_keep]
        y = y[indices_to_keep]
        print("New class distribution after removing samples:", pd.Series(y).value_counts())

    if len(np.unique(y)) < 2:
        print("⚠️   Insufficient number of classes (less than 2) for training. Skipping model training and evaluation.")
        return None, None, None, None

    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Scale features
    scaler = RobustScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Save the scaler
    import joblib
    joblib.dump(scaler, 'scaler.pkl')
    print("Scaler saved to scaler.pkl")

    return X_train_scaled, X_test_scaled, y_train, y_test

def compute_weights(y_train):
    """Computes class weights for handling imbalance in training."""
    class_weights = compute_class_weight(class_weight='balanced', classes=np.unique(y_train), y=y_train)
    return {i: class_weights[i] for i in range(len(class_weights))}

def build_model(input_shape, num_classes):
    """Builds a refined neural network model."""
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(128, activation='relu', input_shape=(input_shape,), kernel_regularizer=tf.keras.regularizers.l2(0.001)),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(64, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.001)),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(32, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.001)),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dense(num_classes, activation='softmax')
    ])

    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

def train_and_save_model(model, X_train, y_train, X_test, y_test, class_weight_dict, model_save_path): # Changed class_weights to class_weight_dict
    """Trains model with early stopping, evaluates, and saves it."""
    early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

    model.fit(X_train, y_train, epochs=100, batch_size=16, validation_data=(X_test, y_test), class_weight=class_weight_dict, callbacks=[early_stopping]) # Changed class_weights to class_weight_dict

    # Evaluation
    y_pred = np.argmax(model.predict(X_test), axis=-1)
    y_pred_probs = model.predict(X_test, verbose=0)

    # Calculate AUC manually
    auc_scores = []
    for i in range(len(np.unique(y))):
        if i in np.unique(y_pred):  # Only calculate AUC if the class is present in predictions
            try:
                auc = roc_auc_score(y_test == i, y_pred_probs[:, i])
                auc_scores.append(auc)
            except ValueError as e:
                print(f"Error calculating AUC for class {i}: {e}")
                auc_scores.append(0)  # Set AUC to 0 on error

    mean_auc = np.nanmean(auc_scores) if auc_scores else 0  # Handle empty AUC scores

    # Calculate F1 score
    f1 = f1_score(y_test, y_pred, average='weighted')

    print("\nClassification Report:\n", classification_report(y_test, y_pred, zero_division=0))
    print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred, labels=np.unique(y)))
    print("\nMean AUC:", mean_auc)
    print("\nWeighted F1 Score:", f1)

    # Delete old model if it exists
    if os.path.exists(model_save_path):
        os.remove(model_save_path)
        print(f"Old model deleted from {model_save_path}")

    model.save(model_save_path)
    print(f"✅ Model saved to {model_save_path}")

# Pipeline Execution
X, y, feature_names = load_and_preprocess_data(DATA_PATH)
X_resampled, y_resampled = balance_data(X, y)
X_train_scaled, X_test_scaled, y_train, y_test = prepare_data(X_resampled, y_resampled)

# Check if prepare_data returned valid training data
if X_train_scaled is not None:
    class_weight_dict = compute_weights(y_train)
    model = build_model(X_train_scaled.shape[1], len(np.unique(y_train)))
    train_and_save_model(model, X_train_scaled, y_train, X_test_scaled, y_test, class_weight_dict, MODEL_SAVE_PATH)
else:
    print("Skipping model training due to insufficient data.")

print("Feature Names:", feature_names)
