import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

def generate_heart_disease_eda_visuals(data_path, output_dir):
    """
    Generates Exploratory Data Analysis (EDA) visualizations for the Heart Disease dataset.

    Args:
        data_path (str): Path to the 'heart.csv' dataset.
        output_dir (str): Directory where the generated figures will be saved.
    """
    try:
        # Load dataset
        df = pd.read_csv(data_path)
        print(f"Dataset loaded from {data_path}")

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        print(f"Output directory created/ensured at: {output_dir}")

        target_col = 'target' # As specified in the description for heart disease

        # --- Figure 3.1: Class Distribution of Heart Disease Target Variable ---
        plt.figure(figsize=(6, 4))
        class_counts = df[target_col].value_counts()
        # Assuming target=0 is 'No Heart Disease' and target=1 is 'Heart Disease'
        labels = ['No Heart Disease', 'Heart Disease']
        sns.barplot(x=labels, y=class_counts.values, palette="viridis")
        for i, v in enumerate(class_counts.values):
            plt.text(i, v + 5, str(v), ha='center', va='bottom', fontweight='bold')
        plt.title("Figure 3.1: Class Distribution of Heart Disease Target Variable")
        plt.xlabel("Heart Disease Presence")
        plt.ylabel("Number of Instances")
        plt.tight_layout()
        fig_path_3_1 = os.path.join(output_dir, "fig3_1_heart_class_distribution.png")
        plt.savefig(fig_path_3_1)
        plt.close()
        print(f"Generated {fig_path_3_1}")

        # --- Figure 3.2: Correlation Matrix of Heart Disease Dataset ---
        plt.figure(figsize=(12, 10))
        corr_matrix = df.corr()
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool)) # Mask to show only upper triangle, for clarity
        sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", mask=mask, linewidths=.5, cbar_kws={"shrink": .8})
        plt.title("Figure 3.2: Correlation Matrix of Heart Disease Dataset")
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        fig_path_3_2 = os.path.join(output_dir, "fig3_2_heart_correlation_matrix.png")
        plt.savefig(fig_path_3_2)
        plt.close()
        print(f"Generated {fig_path_3_2}")

        print("\n[INFO] All specified EDA visualizations for Heart Disease generated successfully.")

    except FileNotFoundError:
        print(f"Error: Dataset not found at {data_path}. Please check the path and ensure it's correct.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # --- IMPORTANT: YOU MUST UPDATE THESE PATHS ---
    # Specify the correct path to your 'heart.csv' dataset
    heart_data_path = r"C:\Users\USER\Documents\GitHub\Multi-Disease-Diagnosis-System-v0\backend\dataset\Heart-Disease\heart.csv" # <--- REPLACE THIS WITH YOUR ACTUAL DATASET PATH
    # Specify the directory where you want to save the generated images
    heart_output_dir = r"C:\Users\USER\Documents\GitHub\Multi-Disease-Diagnosis-System-v0\backend\scripts\heart_scripts\img" # <--- REPLACE THIS WITH YOUR DESIRED OUTPUT DIRECTORY

    generate_heart_disease_eda_visuals(heart_data_path, heart_output_dir)