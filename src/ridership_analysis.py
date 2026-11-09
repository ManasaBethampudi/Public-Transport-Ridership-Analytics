
import pandas as pd
from pathlib import Path

# Load cleaned dataset
df = pd.read_csv("data/cleaned_ridership_data.csv")

# Create output folder if needed
Path("results").mkdir(exist_ok=True)

# 1. Ridership by time period
time_analysis = (
    df.groupby("Time_Period")["Passenger_Count"]
    .agg(["sum", "mean", "count"])
    .reset_index()
    .rename(columns={
        "sum": "Total_Passengers",
        "mean": "Average_Passengers",
        "count": "Records"
    })
    .sort_values("Total_Passengers", ascending=False)
)

# 2. Ridership by route
route_analysis = (
    df.groupby("Route")["Passenger_Count"]
    .agg(["sum", "mean", "count"])
    .reset_index()
    .rename(columns={
        "sum": "Total_Passengers",
        "mean": "Average_Passengers",
        "count": "Records"
    })
    .sort_values("Total_Passengers", ascending=False)
)

# 3. Ridership by day
day_analysis = (
    df.groupby("Day")["Passenger_Count"]
    .agg(["sum", "mean", "count"])
    .reset_index()
    .rename(columns={
        "sum": "Total_Passengers",
        "mean": "Average_Passengers",
        "count": "Records"
    })
    .sort_values("Total_Passengers", ascending=False)
)

# Save analysis results
time_analysis.to_csv("results/ridership_by_time.csv", index=False)
route_analysis.to_csv("results/ridership_by_route.csv", index=False)
day_analysis.to_csv("results/ridership_by_day.csv", index=False)

# Display results
print("\n=== RIDERSHIP BY TIME PERIOD ===")
print(time_analysis.to_string(index=False))

print("\n=== RIDERSHIP BY ROUTE ===")
print(route_analysis.to_string(index=False))

print("\n=== RIDERSHIP BY DAY ===")
print(day_analysis.to_string(index=False))

print("\nPeak time period:",
      time_analysis.iloc[0]["Time_Period"])

print("Busiest route:",
      route_analysis.iloc[0]["Route"])

print("\nAnalysis CSV files saved in results/ folder.")
