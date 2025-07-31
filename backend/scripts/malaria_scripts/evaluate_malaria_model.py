import tensorflow as tf
import os
import numpy as np
from tensorflow.keras.utils import Sequence
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import cv2  # Import OpenCV for image processing
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# --- Configuration and File Paths ---
MODEL_PATH = r"C:\Users\USER\Documents\GitHub\Multi-Disease-Diagnosis-System-v0\backend\models\multi_class_malaria_model\multi_class_malaria_model.h5"
TEST_DATA_DIR = r"C:\Users\USER\Documents\GitHub\Multi-Disease-Diagnosis-System-v0\backend\dataset\malaria\test"

image_size = (128, 128)
batch_size = 32

CLASS_NAMES = ['Parasitized', 'Uninfected', 'NonBloodSmear']
CLASS_INDICES = {'Parasitized': 0, 'Uninfected': 1, 'NonBloodSmear': 2}
NUM_CLASSES = len(CLASS_NAMES)

# --- Custom Data Generator for Evaluation (without augmentation, but with preprocessing) ---
class CustomEvaluationDataGenerator(Sequence):
    def __init__(self, image_paths, labels, image_size=(128, 128), batch_size=32, shuffle=False):
        self.image_paths = image_paths
        self.labels = labels
        self.image_size = image_size
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.on_epoch_end()

    def __len__(self):
        return int(np.ceil(len(self.image_paths) / self.batch_size))

    def __getitem__(self, index):
        start_index = index * self.batch_size
        end_index = min((index + 1) * self.batch_size, len(self.image_paths))
        batch_x = self.image_paths[start_index:end_index]
        batch_y = self.labels[start_index:end_index]
        return self.__data_generation(batch_x, batch_y)

    def on_epoch_end(self):
        if self.shuffle:
            self.indices = np.arange(len(self.image_paths))
            np.random.shuffle(self.indices)
        else:
            self.indices = np.arange(len(self.image_paths))

    def __data_generation(self, batch_x, batch_y):
        current_batch_size = len(batch_x)
        X = np.empty((current_batch_size, *self.image_size, 3))
        y = np.array(batch_y)

        for i, img_path in enumerate(batch_x):
            img = load_img(img_path, target_size=self.image_size)
            img_array = img_to_array(img)

            img_array = (img_array).astype(np.uint8)
            img_array = cv2.GaussianBlur(img_array, (3, 3), 0)
            img_array = cv2.addWeighted(img_array, 1.5, cv2.GaussianBlur(img_array, (5, 5), 0), -0.5, 0)
            img_array = img_array / 255.0

            X[i,] = img_array

        return X, tf.keras.utils.to_categorical(y, num_classes=NUM_CLASSES)


# --- Function to create filepaths and labels ---
def create_filepaths_and_labels(directory, class_indices):
    image_paths = []
    labels = []
    found_classes = set() # To track which classes were actually found
    print(f"\n--- Scanning directory: {directory} ---")
    for class_name, class_index in class_indices.items():
        class_dir = os.path.join(directory, class_name)
        print(f"Checking for class directory: {class_dir}")
        if os.path.exists(class_dir):
            class_images = [
                os.path.join(class_dir, filename)
                for filename in os.listdir(class_dir)
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif'))
            ]
            if class_images:
                image_paths.extend(class_images)
                labels.extend([class_index] * len(class_images))
                found_classes.add(class_name)
                print(f"Found {len(class_images)} images for class '{class_name}'.")
            else:
                print(f"No valid images found in directory: {class_dir}")
        else:
            print(f"Class directory NOT found: {class_dir}")
    print(f"--- Finished scanning. Found classes: {list(found_classes)} ---")
    return image_paths, labels

# --- 1. Load the Trained Model ---
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    print(f"Model loaded successfully from: {MODEL_PATH}")
except Exception as e:
    print(f"Error loading model: {e}")
    print("Please ensure the model path is correct and the model file exists.")
    exit()

# --- 2. Prepare the Test Data ---
print(f"Creating filepaths and labels for test data from: {TEST_DATA_DIR}...")
test_image_paths, test_labels = create_filepaths_and_labels(TEST_DATA_DIR, CLASS_INDICES)

# --- DEBUGGING: Check what was actually loaded ---
print(f"\nTotal images loaded for testing: {len(test_image_paths)}")
if not test_image_paths:
    print(f"Error: No images found in the test directory: {TEST_DATA_DIR}. Please check the path and subfolder structure.")
    exit()

# Verify that all expected class labels are present in `test_labels`
unique_test_labels = np.unique(test_labels)
print(f"Unique numeric labels found in test set: {unique_test_labels}")
if len(unique_test_labels) != NUM_CLASSES:
    print(f"WARNING: Expected {NUM_CLASSES} classes, but found {len(unique_test_labels)} in test data.")
    print("This is likely the cause of your confusion matrix dimension mismatch.")
    # You might want to remap `CLASS_NAMES` and `CLASS_INDICES` here
    # if you decide to proceed with fewer classes for the evaluation.
    # For now, we'll keep the original CLASS_NAMES and let the error persist
    # if the issue isn't resolved by fixing the data.


test_generator = CustomEvaluationDataGenerator(
    test_image_paths,
    test_labels,
    image_size=image_size,
    batch_size=batch_size,
    shuffle=False
)

# Get true labels (original integer labels)
y_true = np.array(test_labels)

# --- 3. Make Predictions ---
print("Making predictions on the test set...")
y_pred_probs = model.predict(test_generator)

# Convert probabilities to class predictions (indices)
y_pred = np.argmax(y_pred_probs, axis=1)

# --- 4. Calculate Performance Metrics ---
print("\n--- Model Performance Metrics ---")

# Overall Accuracy
accuracy = accuracy_score(y_true, y_pred)
print(f"Accuracy: {accuracy:.4f}")

# Precision, Recall, F1-Score for the 'Parasitized' class
parasitized_index = CLASS_INDICES['Parasitized']

precision_per_class = precision_score(y_true, y_pred, average=None, labels=np.arange(NUM_CLASSES), zero_division=0)
recall_per_class = recall_score(y_true, y_pred, average=None, labels=np.arange(NUM_CLASSES), zero_division=0)
f1_per_class = f1_score(y_true, y_pred, average=None, labels=np.arange(NUM_CLASSES), zero_division=0)

# Make sure parasitized_index is valid for the actual `precision_per_class` array size
if parasitized_index < len(precision_per_class):
    precision_parasitized = precision_per_class[parasitized_index]
    recall_parasitized = recall_per_class[parasitized_index]
    f1_parasitized = f1_per_class[parasitized_index]
else:
    print(f"WARNING: Parasitized class (index {parasitized_index}) not found in predictions for per-class metrics.")
    precision_parasitized = np.nan
    recall_parasitized = np.nan
    f1_parasitized = np.nan

print(f"Precision (Parasitized): {precision_parasitized:.4f}")
print(f"Recall (Parasitized): {recall_parasitized:.4f}")
print(f"F1-Score (Parasitized): {f1_parasitized:.4f}")

# --- 5. Generate and Display Confusion Matrix ---
print("\n--- Confusion Matrix ---")
cm = confusion_matrix(y_true, y_pred)
print(cm)

# Adjust class names for confusion matrix plot if classes are missing in test data
actual_classes_in_cm = [CLASS_NAMES[i] for i in sorted(np.unique(y_true))] # Gets the names of classes actually present in y_true
# If cm.shape[0] (number of actual classes) doesn't match len(CLASS_NAMES),
# this indicates a problem with the test data not having all expected classes.

plt.figure(figsize=(8, 6))
# Use the actual_classes_in_cm for plotting if there's a mismatch
if cm.shape[0] != NUM_CLASSES:
    print(f"Plotting Confusion Matrix for {cm.shape[0]} classes found in test data.")
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=actual_classes_in_cm, yticklabels=actual_classes_in_cm)
else:
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES)
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.title('Confusion Matrix for Malaria Diagnosis')
plt.show()

# --- 6. Extract values for your table ---
print("\n--- Confusion Matrix Values for Table ---")
# Only attempt to access indices if they are within the bounds of the actual CM
if cm.shape == (NUM_CLASSES, NUM_CLASSES):
    TP_value = cm[CLASS_INDICES['Parasitized'], CLASS_INDICES['Parasitized']]
    FN1_value = cm[CLASS_INDICES['Parasitized'], CLASS_INDICES['Uninfected']]
    FN2_value = cm[CLASS_INDICES['Parasitized'], CLASS_INDICES['NonBloodSmear']]

    FP1_value = cm[CLASS_INDICES['Uninfected'], CLASS_INDICES['Parasitized']]
    TN_value = cm[CLASS_INDICES['Uninfected'], CLASS_INDICES['Uninfected']]
    FN3_value = cm[CLASS_INDICES['Uninfected'], CLASS_INDICES['NonBloodSmear']]

    FP2_value = cm[CLASS_INDICES['NonBloodSmear'], CLASS_INDICES['Parasitized']]
    FP3_value = cm[CLASS_INDICES['NonBloodSmear'], CLASS_INDICES['Uninfected']]
    TN_NS_value = cm[CLASS_INDICES['NonBloodSmear'], CLASS_INDICES['NonBloodSmear']]

    print(f"TP (Parasitized): {TP_value}")
    print(f"FN1 (Parasitized misclassified as Uninfected): {FN1_value}")
    print(f"FN2 (Parasitized misclassified as Non-Smear): {FN2_value}")
    print(f"FP1 (Uninfected misclassified as Parasitized): {FP1_value}")
    print(f"TN (Uninfected, correct identification): {TN_value}")
    print(f"FN3 (Uninfected misclassified as Non-Smear): {FN3_value}")
    print(f"FP2 (Non-Smear misclassified as Parasitized): {FP2_value}")
    print(f"FP3 (Non-Smear misclassified as Uninfected): {FP3_value}")
    print(f"TN (Non-Smear, correct identification): {TN_NS_value}")
else:
    print("Cannot extract individual confusion matrix values as expected due to dimension mismatch.")
    print(f"Actual Confusion Matrix Shape: {cm.shape}")
    print("Please inspect the printed confusion matrix above and your test data structure.")

print("\nScript execution complete.")