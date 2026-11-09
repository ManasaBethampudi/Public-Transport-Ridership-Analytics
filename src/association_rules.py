
from pathlib import Path
import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "BUS_DATA_FEB_2018.csv"
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# Read only the columns needed for mining
columns = [
    "Card_Type",
    "Travel_Mode",
    "Bus_Service_Number",
    "Direction",
    "Boarding_stop_stn",
    "Alighting_stop_stn",
    "Ride_start_date",
    "Ride_start_time",
]

print("Loading original February 2018 dataset...")
df = pd.read_csv(DATA_FILE, usecols=columns, dtype=str)
print("Original records:", len(df))

# Derive day and time period from the actual ride date/time
dates = pd.to_datetime(
    df["Ride_start_date"], dayfirst=True, errors="coerce"
)
times = pd.to_datetime(
    df["Ride_start_time"], format="%H:%M:%S", errors="coerce"
)

df["Day"] = dates.dt.day_name()
hours = times.dt.hour

df["Time_Period"] = "Night"
df.loc[hours.between(5, 11), "Time_Period"] = "Morning"
df.loc[hours.between(12, 16), "Time_Period"] = "Afternoon"
df.loc[hours.between(17, 21), "Time_Period"] = "Evening"

# Limit the mining workload while using real source records.
# A fixed random seed makes the sample reproducible.
sample_size = min(50000, len(df))
if len(df) > sample_size:
    df = df.sample(n=sample_size, random_state=42)

print("Records used for mining:", len(df))

feature_columns = {
    "Card_Type": "CardType",
    "Travel_Mode": "Mode",
    "Bus_Service_Number": "Service",
    "Direction": "Direction",
    "Boarding_stop_stn": "Boarding",
    "Alighting_stop_stn": "Alighting",
    "Day": "Day",
    "Time_Period": "Time",
}

transactions = []
for _, row in df.iterrows():
    items = []
    for column, prefix in feature_columns.items():
        value = row[column]
        if pd.notna(value) and str(value).strip():
            items.append(f"{prefix}_{str(value).strip()}")
    if len(items) >= 2:
        transactions.append(items)

if not transactions:
    raise ValueError("No valid transactions were created.")

print("Encoding transactions...")
encoder = TransactionEncoder()
encoded = encoder.fit(transactions).transform(
    transactions, sparse=True
)
basket = pd.DataFrame.sparse.from_spmatrix(
    encoded, columns=encoder.columns_
)

print("Mining frequent itemsets...")
frequent_itemsets = apriori(
    basket,
    min_support=0.01,
    use_colnames=True,
    max_len=3,
    low_memory=True,
)

if frequent_itemsets.empty:
    raise ValueError(
        "No frequent itemsets found. Review min_support."
    )

# Save readable frequent itemsets
itemsets_output = frequent_itemsets.copy()
itemsets_output["itemsets"] = itemsets_output["itemsets"].apply(
    lambda items: ", ".join(sorted(items))
)
itemsets_output.to_csv(
    RESULTS_DIR / "frequent_itemsets.csv", index=False
)

print("Generating association rules...")
rules = association_rules(
    frequent_itemsets,
    metric="confidence",
    min_threshold=0.60,
)

if not rules.empty:
    rules["antecedents"] = rules["antecedents"].apply(
        lambda items: ", ".join(sorted(items))
    )
    rules["consequents"] = rules["consequents"].apply(
        lambda items: ", ".join(sorted(items))
    )
    rules = rules.sort_values(
        ["confidence", "lift"], ascending=False
    )
    rules.to_csv(
        RESULTS_DIR / "association_rules.csv", index=False
    )
    print("Rules generated:", len(rules))
    print(
        rules[
            ["antecedents", "consequents",
             "support", "confidence", "lift"]
        ].head(10).to_string(index=False)
    )
else:
    # Write an empty file with the expected rule columns
    pd.DataFrame(
        columns=[
            "antecedents", "consequents", "support",
            "confidence", "lift",
        ]
    ).to_csv(RESULTS_DIR / "association_rules.csv", index=False)
    print("No rules met the confidence threshold.")

print("Frequent itemsets:", len(frequent_itemsets))
print("Results saved in:", RESULTS_DIR)

