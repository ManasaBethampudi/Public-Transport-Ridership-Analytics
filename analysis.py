
import pandas as pd
import os

# Load February transport data
file_path = "data/BUS_DATA_FEB_2018.csv"
df = pd.read_csv(file_path)

print("========== DATA OVERVIEW ==========")
print("Total records:", len(df))
print("Total columns:", len(df.columns))
print("Missing values:", df.isnull().sum().sum())

# Convert dates correctly
df["Ride_start_date"] = pd.to_datetime(
    df["Ride_start_date"], dayfirst=True, errors="coerce"
)

# Create output folder
os.makedirs("results", exist_ok=True)

# 1. Daily ridership
daily = df.groupby(
    df["Ride_start_date"].dt.strftime("%Y-%m-%d")
).size().reset_index(name="Total_Rides")

daily.columns = ["Date", "Total_Rides"]
daily.to_csv("results/daily_ridership.csv", index=False)

# 2. Travel mode analysis
travel = df["Travel_Mode"].value_counts().reset_index()
travel.columns = ["Travel_Mode", "Total_Rides"]
travel.to_csv("results/travel_mode_analysis.csv", index=False)

# 3. Popular boarding stops
boarding = df["Boarding_stop_stn"].value_counts().head(10)
boarding = boarding.reset_index()
boarding.columns = ["Boarding_Stop", "Total_Rides"]
boarding.to_csv("results/top_boarding_stops.csv", index=False)

# 4. Popular alighting stops
alighting = df["Alighting_stop_stn"].value_counts().head(10)
alighting = alighting.reset_index()
alighting.columns = ["Alighting_Stop", "Total_Rides"]
alighting.to_csv("results/top_alighting_stops.csv", index=False)

# 5. Bus service analysis
services = df["Bus_Service_Number"].value_counts().head(10)
services = services.reset_index()
services.columns = ["Bus_Service_Number", "Total_Rides"]
services.to_csv("results/top_bus_services.csv", index=False)

# 6. Card type analysis
cards = df["Card_Type"].value_counts().reset_index()
cards.columns = ["Card_Type", "Total_Rides"]
cards.to_csv("results/card_type_analysis.csv", index=False)

print("\n========== DAILY RIDERSHIP ==========")
print(daily.to_string(index=False))

print("\n========== TOP 10 BOARDING STOPS ==========")
print(boarding.to_string(index=False))

print("\n========== TRAVEL MODE ANALYSIS ==========")
print(travel.to_string(index=False))

print("\nAnalysis completed successfully!")
print("All result files are saved in the results folder.")
