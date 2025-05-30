import os

# Define the paths
directories = {
    "Parasitized": r"C:\Users\USER\Documents\GitHub\malaria-expert-system\backend\dataset\malaria\train\Parasitized",
    "Uninfected": r"C:\Users\USER\Documents\GitHub\malaria-expert-system\backend\dataset\malaria\train\Uninfected",
    "NonBloodSmear": r"C:\Users\USER\Documents\GitHub\malaria-expert-system\backend\dataset\malaria\train\NonBloodSmear"
}

# Function to count image files in a directory (including subfolders)
def count_images(directory):
    count = 0
    for root, _, files in os.walk(directory):
        count += sum(1 for file in files if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')))
    return count

# Count and display results
for label, path in directories.items():
    num_images = count_images(path)
    print(f"📂 {label}: {num_images} images")
