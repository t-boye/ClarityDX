import os
import cv2
import random
import matplotlib.pyplot as plt

# Define dataset path
dataset_path = r"C:\Users\USER\Documents\GitHub\malaria-expert-system\backend\dataset\malaria\train"

# Define categories
categories = ["Parasitized", "Uninfected"]

# Function to display random images
def display_images():
    fig, axes = plt.subplots(2, 5, figsize=(12, 6))  # 2 rows, 5 images each

    for i, category in enumerate(categories):
        category_path = os.path.join(dataset_path, category)

        if not os.path.exists(category_path):
            print(f"⚠️ Warning: '{category}' folder not found!")
            continue

        # Get random 5 images from each category
        image_files = random.sample(os.listdir(category_path), 5)

        for j, img_name in enumerate(image_files):
            img_path = os.path.join(category_path, img_name)
            img = cv2.imread(img_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert from BGR to RGB

            axes[i, j].imshow(img)
            axes[i, j].set_title(f"{category}")
            axes[i, j].axis("off")

    plt.tight_layout()
    plt.show()

# Run visualization
display_images()
