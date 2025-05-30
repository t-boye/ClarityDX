import pickle

file_path = r"C:\Users\USER\Documents\GitHub\malaria-expert-system\backend\models\ckd_model\ckd_feature_names.pkl"

try:
    with open(file_path, 'rb') as f:
        feature_names = pickle.load(f)

    print(f"The number of columns in {file_path} is: {len(feature_names)}")
    print("Column Names:")
    for name in feature_names:
        print(name)

except FileNotFoundError:
    print(f"Error: File not found at {file_path}")
except Exception as e:
    print(f"An error occurred: {e}")