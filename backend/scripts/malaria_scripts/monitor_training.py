import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.callbacks import CSVLogger, EarlyStopping, ModelCheckpoint
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.utils import Sequence

# --- Define Data Directories ---
train_dir = r"C:\Users\USER\Documents\GitHub\malaria-expert-system\backend\dataset\malaria\train"
image_size = (128, 128)  # Image dimensions
batch_size = 32  # Batch size for training

# --- Custom Data Generator ---
class CustomDataGenerator(Sequence):
    def __init__(self, directory, image_size=(128, 128), batch_size=32, shuffle=True):
        self.directory = directory
        self.image_size = image_size
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.image_paths = []
        self.labels = []
        self.class_indices = {'Parasitized': 0, 'Uninfected': 1, 'NonBloodSmear': 2}
        self._load_data()
        self.on_epoch_end()

    def _load_data(self):
        # Load images and labels from the directory
        for class_name, class_index in self.class_indices.items():
            class_dir = os.path.join(self.directory, class_name)
            if os.path.exists(class_dir):
                for filename in os.listdir(class_dir):
                    if filename.endswith('.jpg') or filename.endswith('.png'):
                        self.image_paths.append(os.path.join(class_dir, filename))
                        self.labels.append(class_index)

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
            img_array = img_to_array(img) / 255.0  # Normalize to [0, 1]
            X[i,] = img_array

        return X, tf.keras.utils.to_categorical(y, num_classes=3)  # One-hot encoding for 3 classes

# --- Create Data Generators ---
train_generator = CustomDataGenerator(train_dir, image_size=image_size, batch_size=batch_size)
validation_generator = CustomDataGenerator(train_dir, image_size=image_size, batch_size=batch_size)

# --- Updated CNN Model for Multi-Class Classification ---
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

    tf.keras.layers.Dense(3, activation="softmax")  # 3 classes: Parasitized, Uninfected, NonBloodSmear
])

# --- Compile the Model ---
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
    loss="categorical_crossentropy",  # Multi-class loss function
    metrics=["accuracy"]
)

# --- Callbacks for Training ---
log_dir = r"C:\Users\USER\Documents\GitHub\malaria-expert-system\backend\logs"
os.makedirs(log_dir, exist_ok=True)  # Ensure the directory exists
log_file = os.path.join(log_dir, "training_log.csv")
csv_logger = CSVLogger(log_file, append=True)

checkpoint_path = r"C:\Users\USER\Documents\GitHub\malaria-expert-system\backend\models\multi_class_malaria_model.h5"
callbacks = [
    EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True),
    ModelCheckpoint(filepath=checkpoint_path, monitor='val_loss', save_best_only=True),
    csv_logger  # Add CSV logger to callbacks
]

# --- Train the Model ---
model.fit(
    train_generator,
    validation_data=validation_generator,
    epochs=20,
    callbacks=callbacks,
    verbose=1  # Print progress for each epoch
)

print(f"✅ Model saved successfully at: {checkpoint_path}")
print(f"Training metrics logged to: {log_file}")