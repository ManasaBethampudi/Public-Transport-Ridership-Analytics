
import pandas as pd

file_path = "data/ridership_data.csv"

df = pd.read_csv(file_path)

print("Dataset loaded successfully!")
print("\nFirst 5 records:")
print(df.head())

print("\nDataset shape:")
print(df.shape)

print("\nColumn names:")
print(df.columns.tolist())

print("\nMissing values:")
print(df.isnull().sum())
