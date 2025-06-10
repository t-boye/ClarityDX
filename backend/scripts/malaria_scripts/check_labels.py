import os
import matplotlib.pyplot as plt
from PIL import Image
import random

def verify_labels_from_directories(dataset_path, num_images_per_category=5):
    """
    Verifies image labels based on directory structure.

    Args:
        dataset_path (str): Path to the dataset directory (e.g., "dataset/train").
        num_images_per_category (int): Number of images to display per category.
    """
    categories = ["Parasitized", "Uninfected", "NonBloodSmear"]
    fig = plt.figure(figsize=(10, 5))

    for category in categories:
        # Define category_path inside the loop
        category_path = os.path.join(dataset_path, category)
        
        if not os.path.exists(category_path):
            print(f"Warning: Directory {category_path} does not exist.")
            continue

        image_files = os.listdir(category_path)
        # Shuffle the list of image files randomly
        random.shuffle(image_files)
        # Select the desired number of images
        selected_images = image_files[:num_images_per_category]

        for i, image_file in enumerate(selected_images):
            image_path = os.path.join(category_path, image_file)
            try:
                img = Image.open(image_path)
                plt.subplot(2, num_images_per_category, categories.index(category) * num_images_per_category + i + 1)
                plt.imshow(img)
                plt.title(f"Label: {category}")
                plt.axis("off")
            except Exception as e:
                print(f"Error processing {image_path}: {e}")

    plt.tight_layout()
    plt.show()

# Usage
dataset_path = r"C:\Users\USER\Documents\GitHub\Multi-Disease-Diagnosis-System-v0\backend\dataset\malaria\train" # change to your path
verify_labels_from_directories(dataset_path, num_images_per_category=5)