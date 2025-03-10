import os
import kaggle
import pandas as pd

# Set Kaggle dataset
dataset = "aungpyaeap/supermarket-sales"

# Define the target directory
download_path = r"C:\66"

# Ensure the directory exists
os.makedirs(download_path, exist_ok=True)

# Download the dataset
kaggle.api.dataset_download_files(dataset, path=download_path, unzip=True)

# Load CSV
file_path = os.path.join(download_path, "supermarket_sales.csv")
df = pd.read_csv(file_path)

# Display first few rows
print(df.head())
