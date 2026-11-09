
from pathlib import Path
from datetime import date

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# Project paths
ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "BUS_DATA_FEB_2018.csv"
RESULTS_DIR = ROOT / "results"

app = FastAPI(
    title="Public Transport Ridership Analytics API",
    description="API for public transport ridership and association-rule analysis",
    version="1.0.0",
)

# Allow React development server to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load only columns needed by the dashboard
REQUIRED_COLUMNS = [
    "Card_Number",
    "Card_Type",
    "Travel_Mode",
    "Bus_Service_Number",
    "Boarding_stop_stn",
    "Alighting_stop_stn",
    "Ride_start_date",
]

df = None
load_error = None


@app.on_event("startup")
def load_dataset():
    global df, load_error

    if not DATA_FILE.exists():
        load_error = f"Dataset not found: {DATA_FILE}"
        print(load_error)
        return

    try:
        data = pd.read_csv(
            DATA_FILE,
            usecols=REQUIRED_COLUMNS,
            low_memory=False,
        )

        data["Ride_start_date"] = pd.to_datetime(
            data["Ride_start_date"],
            dayfirst=True,
            errors="coerce",
        )

        data = data.dropna(subset=["Ride_start_date"])

        df = data
        load_error = None

        print(f"Dataset loaded: {len(df):,} ride records")

    except Exception as exc:
        load_error = str(exc)
        print(f"Dataset loading error: {exc}")


def top_counts(data, column, name):
    result = (
        data[column]
        .dropna()
        .astype(str)
        .value_counts()
        .head(10)
    )

    return [
        {"name": str(key), "rides": int(value)}
        for key, value in result.items()
    ]


def get_association_rules():
    path = RESULTS_DIR / "association_rules.csv"

    if not path.exists():
        return []

    try:
        rules_df = pd.read_csv(path)
        rules_df.columns = [
            str(column).strip().lower()
            for column in rules_df.columns
        ]

        # Support common column-name variations
        aliases = {
            "antecedents": ["antecedents", "antecedent"],
            "consequents": ["consequents", "consequent"],
            "support": ["support"],
            "confidence": ["confidence"],
            "lift": ["lift"],
        }

        chosen = {}
        for target, options in aliases.items():
            for option in options:
                if option in rules_df.columns:
                    chosen[target] = option
                    break

        required = ["antecedents", "consequents", "support", "confidence", "lift"]

        if not all(key in chosen for key in required):
            print("Association rules CSV has unexpected column names.")
            return []

        rules = []

        for _, row in rules_df.head(200).iterrows():
            rules.append({
                "antecedents": str(row[chosen["antecedents"]]),
                "consequents": str(row[chosen["consequents"]]),
                "support": float(row[chosen["support"]]),
                "confidence": float(row[chosen["confidence"]]),
                "lift": float(row[chosen["lift"]]),
            })

        return rules

    except Exception as exc:
        print(f"Could not read association rules: {exc}")
        return []


@app.get("/")
def home():
    return {
        "message": "Public Transport Ridership Analytics API",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/api/health")
def health():
    return {
        "status": "ok" if df is not None else "dataset_unavailable",
        "dataset_loaded": df is not None,
        "total_records": int(len(df)) if df is not None else 0,
        "error": load_error,
    }


@app.get("/api/dashboard")
def dashboard(
    start_date: date = Query(default=date(2018, 2, 1)),
    end_date: date = Query(default=date(2018, 2, 28)),
):
    if df is None:
        raise HTTPException(
            status_code=503,
            detail=load_error or "Dataset is not loaded.",
        )

    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="start_date must be before or equal to end_date.",
        )

    filtered = df[
        (df["Ride_start_date"].dt.date >= start_date)
        & (df["Ride_start_date"].dt.date <= end_date)
    ]

    total_rides = len(filtered)

    daily_counts = (
        filtered.groupby(filtered["Ride_start_date"].dt.strftime("%Y-%m-%d"))
        .size()
        .reset_index(name="total_rides")
    )

    daily_ridership = [
        {
            "date": str(row.iloc[0]),
            "total_rides": int(row.iloc[1]),
        }
        for _, row in daily_counts.iterrows()
    ]

    travel_counts = filtered["Travel_Mode"].dropna().value_counts()
    travel_modes = [
        {"name": str(key), "rides": int(value)}
        for key, value in travel_counts.items()
    ]

    card_counts = filtered["Card_Type"].dropna().value_counts()
    card_types = [
        {"name": str(key), "rides": int(value)}
        for key, value in card_counts.items()
    ]

    service_counts = filtered["Bus_Service_Number"].dropna().value_counts().head(10)
    services = [
        {"name": str(key), "rides": int(value)}
        for key, value in service_counts.items()
    ]

    return {
        "summary": {
            "total_rides": int(total_rides),
            "unique_cards": int(filtered["Card_Number"].nunique()),
            "bus_services": int(filtered["Bus_Service_Number"].nunique()),
            "boarding_stops": int(filtered["Boarding_stop_stn"].nunique()),
        },
        "daily_ridership": daily_ridership,
        "top_boarding_stops": top_counts(
            filtered, "Boarding_stop_stn", "name"
        ),
        "top_alighting_stops": top_counts(
            filtered, "Alighting_stop_stn", "name"
        ),
        "travel_modes": travel_modes,
        "card_types": card_types,
        "top_bus_services": services,
        "association_rules": get_association_rules(),
    }


@app.get("/api/association-rules")
def association_rules():
    return {"association_rules": get_association_rules()}
