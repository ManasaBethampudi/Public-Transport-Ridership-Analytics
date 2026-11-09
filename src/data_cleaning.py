
import pandas as pd
from pathlib import Path

# Load the dataset
df = pd.read_csv("data/ridership_data.csv")

# Remove duplicate records
df = df.drop_duplicates()

# Convert date to datetime format
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# Convert passenger count to numeric
df["Passenger_Count"] = pd.to_numeric(
    df["Passenger_Count"], errors="coerce"
)

# Remove rows with invalid essential values
df = df.dropna(
    subset=["Date", "Time", "Route", "Stop",
            "Passenger_Count", "Day"]
)

# Remove invalid passenger counts
df = df[df["Passenger_Count"] >= 0]

# Convert time into categories
def get_time_period(time):
    hour = int(time.split(":")[0])

    if 5 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 17:
        return "Afternoon"
    elif 17 <= hour < 21:
        return "Evening"
    else:
        return "Night"

df["Time_Period"] = df["Time"].apply(get_time_period)

# Categorize passenger volume
def get_ridership_level(count):
    if count >= 70:
        return "High"
    elif count >= 40:
        return "Medium"
    else:
        return "Low"

df["Ridership_Level"] = df["Passenger_Count"].apply(
    get_ridership_level
)

# Save the cleaned dataset
output_path = Path("data/cleaned_ridership_data.csv")
df.to_csv(output_path, index=False)

print("Data cleaning completed successfully!")
print("\nFirst 5 cleaned records:")
print(df.head().to_string(index=False))

print("\nTime period counts:")
print(df["Time_Period"].value_counts())

print("\nRidership level counts:")
print(df["Ridership_Level"].value_counts())

print(f"\nCleaned dataset saved to: {output_path}")
print(f"Total records: {len(df)}")
