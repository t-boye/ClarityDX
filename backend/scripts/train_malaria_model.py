import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import os
import numpy as np
from tensorflow.keras.utils import Sequence
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import cv2  # Import OpenCV for image processing
from sklearn.model_selection import train_test_split

# --- Define Data Directories ---
train_dir = r"C:\Users\USER\Documents\GitHub\malaria-expert-system\backend\dataset\malaria\train"
image_size = (128, 128)  # Image dimensions
batch_size = 32  # Batch size for training

# --- Custom Data Generator with Augmentation and Preprocessing ---
class CustomDataGenerator(Sequence):
    def __init__(self, image_paths, labels, image_size=(128, 128), batch_size=32, shuffle=True):
        self.image_paths = image_paths
        self.labels = labels
        self.image_size = image_size
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.on_epoch_end()
        self.datagen = ImageDataGenerator(
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode='nearest',
            brightness_range=[0.8, 1.2],
            channel_shift_range=20.0,
        )

    def __len__(self):
        return int(np.floor(len(self.image_paths) / self.batch_size))

    def __getitem__(self, index):
        batch_x = self.image_paths[index * self.batch_size:(index + 1) * self.batch_size]
        batch_y = self.labels[index * self.batch_size:(index + 1) * self.batch_size]
        return self.__data_generation(batch_x, batch_y)

    def on_epoch_end(self):
        if self.shuffle:
            temp = list(zip(self.image_paths, self.labels))
            np.random.shuffle(temp)
            self.image_paths, self.labels = zip(*temp)

    def __data_generation(self, batch_x, batch_y):
        X = np.empty((self.batch_size, *self.image_size, 3))
        y = np.array(batch_y)

        for i, img_path in enumerate(batch_x):
            img = load_img(img_path, target_size=self.image_size)
            img_array = img_to_array(img) / 255.0

            img_array = (img_array * 255).astype(np.uint8)
            img_array = cv2.GaussianBlur(img_array, (3, 3), 0)
            img_array = cv2.addWeighted(img_array, 1.5, cv2.GaussianBlur(img_array, (5, 5), 0), -0.5, 0)
            img_array = img_array / 255.0

            X[i,] = img_array

        return X, tf.keras.utils.to_categorical(y, num_classes=3)

# --- Function to create filepaths and labels ---
def create_filepaths_and_labels(directory, class_indices):
    image_paths = []
    labels = []
    for class_name, class_index in class_indices.items():
        class_dir = os.path.join(directory, class_name)
        if os.path.exists(class_dir):
            for filename in os.listdir(class_dir):
                if filename.endswith('.jpg') or filename.endswith('.png'):
                    image_paths.append(os.path.join(class_dir, filename))
                    labels.append(class_index)
    return image_paths, labels

# --- Create file paths and labels ---
class_indices = {'Parasitized': 0, 'Uninfected': 1, 'NonBloodSmear': 2}
image_paths, labels = create_filepaths_and_labels(train_dir, class_indices)

# --- Split the data into training and validation sets ---
train_paths, val_paths, train_labels, val_labels = train_test_split(
    image_paths, labels, test_size=0.2, random_state=42  # 20% for validation
)

# --- Create Data Generators ---
train_generator = CustomDataGenerator(train_paths, train_labels, image_size=image_size, batch_size=batch_size)
validation_generator = CustomDataGenerator(val_paths, val_labels, image_size=image_size, batch_size=batch_size)

# --- Updated CNN Model with Robust Architecture ---
model = tf.keras.models.Sequential([
    tf.keras.layers.Conv2D(32, (3, 3), activation="relu", input_shape=(128, 128, 3)),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.MaxPooling2D((2, 2)),

    tf.keras.layers.Conv2D(64, (3, 3), activation="relu"),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.MaxPooling2D((2, 2)),

    tf.keras.layers.Conv2D(128, (3, 3), activation="relu"),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.MaxPooling2D((2, 2)),

    tf.keras.layers.Conv2D(256, (3, 3), activation="relu"),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.MaxPooling2D((2, 2)),

    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(512, activation="relu"),
    tf.keras.layers.Dropout(0.5),

    tf.keras.layers.Dense(256, activation="relu"),
    tf.keras.layers.Dropout(0.3),

    tf.keras.layers.Dense(3, activation="softmax")
])

# --- Compile the Model ---
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

# --- Callbacks for Training ---
checkpoint_path = r"C:\Users\USER\Documents\GitHub\malaria-expert-system\backend\models\multi_class_malaria_model\multi_class_malaria_model.h5"
callbacks = [
    EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
    ModelCheckpoint(filepath=checkpoint_path, monitor='val_loss', save_best_only=True)
]

# --- Train the Model ---
model.fit(
    train_generator,
    validation_data=validation_generator,
    epochs=50,
    callbacks=callbacks
)

print(f"✅ Model saved successfully at: {checkpoint_path}")