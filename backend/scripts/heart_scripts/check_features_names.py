import pandas as pd

def print_heart_disease_feature_names(data_path=r"C:\Users\USER\Documents\GitHub\malaria-expert-system\backend\dataset\Heart-Disease\heart.csv"):
    """
    Prints the feature names from a heart disease dataset CSV.

    Args:
        data_path (str): The path to the CSV file.
    """
    try:
        data = pd.read_csv(data_path)
        # Drop any potential ID columns (if any)
        data = data.drop(columns=['id'], errors='ignore')
        # Separate features (X) and target variable (y)
        X = data.drop(columns=["target"])

        print("Feature names of the heart disease dataset:")
        print(X.columns)

    except FileNotFoundError:
        print(f"Error: File not found at {data_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    print_heart_disease_feature_names()