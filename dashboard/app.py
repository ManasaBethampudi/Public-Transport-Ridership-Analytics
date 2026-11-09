
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Public Transport Analytics",
    page_icon="🚌",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent.parent

st.title("🚌 Public Transport Ridership Analytics")
st.caption(
    "Association Rule Mining Pipeline | "
    "Big Data Analytics & Visualization"
)

# Load data
data_file = BASE_DIR / "data" / "cleaned_ridership_data.csv"
rules_file = BASE_DIR / "results" / "association_rules.csv"

df = pd.read_csv(data_file)
df["Passenger_Count"] = pd.to_numeric(
    df["Passenger_Count"], errors="coerce"
)

# Sidebar filters
st.sidebar.header("Filters")

routes = ["All"] + sorted(df["Route"].dropna().unique().tolist())
selected_route = st.sidebar.selectbox("Select Route", routes)

periods = ["All"] + sorted(
    df["Time_Period"].dropna().unique().tolist()
)
selected_period = st.sidebar.selectbox(
    "Select Time Period", periods
)

filtered = df.copy()

if selected_route != "All":
    filtered = filtered[filtered["Route"] == selected_route]

if selected_period != "All":
    filtered = filtered[
        filtered["Time_Period"] == selected_period
    ]

if filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# KPI metrics
total_passengers = int(filtered["Passenger_Count"].sum())
total_routes = filtered["Route"].nunique()
average_count = filtered["Passenger_Count"].mean()
peak_period = (
    filtered.groupby("Time_Period")["Passenger_Count"]
    .sum()
    .idxmax()
)

c1, c2, c3, c4 = st.columns(4)

c1.metric("Passenger Count Total", f"{total_passengers:,}")
c2.metric("Routes", total_routes)
c3.metric("Average Count / Record", f"{average_count:.1f}")
c4.metric("Peak Time Period", peak_period)

st.divider()

# Charts
left, right = st.columns(2)

with left:
    st.subheader("Ridership by Time Period")
    time_data = (
        filtered.groupby("Time_Period")["Passenger_Count"]
        .sum()
        .reset_index()
        .sort_values("Passenger_Count", ascending=False)
    )

    fig_time = px.bar(
        time_data,
        x="Time_Period",
        y="Passenger_Count",
        color="Time_Period",
        title="Total Passenger Count by Time"
    )
    st.plotly_chart(fig_time, use_container_width=True)

with right:
    st.subheader("Ridership by Route")
    route_data = (
        filtered.groupby("Route")["Passenger_Count"]
        .sum()
        .reset_index()
        .sort_values("Passenger_Count", ascending=False)
    )

    fig_route = px.bar(
        route_data,
        x="Route",
        y="Passenger_Count",
        color="Route",
        title="Total Passenger Count by Route"
    )
    st.plotly_chart(fig_route, use_container_width=True)

left2, right2 = st.columns(2)

with left2:
    st.subheader("Ridership Level Distribution")
    level_data = (
        filtered["Ridership_Level"]
        .value_counts()
        .rename_axis("Ridership Level")
        .reset_index(name="Records")
    )

    fig_level = px.pie(
        level_data,
        names="Ridership Level",
        values="Records",
        title="High / Medium / Low"
    )
    st.plotly_chart(fig_level, use_container_width=True)

with right2:
    st.subheader("Day-wise Ridership")
    day_data = (
        filtered.groupby("Day")["Passenger_Count"]
        .sum()
        .reset_index()
        .sort_values("Passenger_Count", ascending=False)
    )

    fig_day = px.bar(
        day_data,
        x="Day",
        y="Passenger_Count",
        title="Passenger Count by Day"
    )
    st.plotly_chart(fig_day, use_container_width=True)

# Association rules
st.divider()
st.header("🔗 Association Rule Mining Results")

if rules_file.exists():
    rules = pd.read_csv(rules_file)

    if not rules.empty:
        rules["confidence_percent"] = (
            rules["confidence"] * 100
        ).round(1)

        st.dataframe(
            rules[
                [
                    "antecedents",
                    "consequents",
                    "support",
                    "confidence_percent",
                    "lift"
                ]
            ].rename(columns={
                "antecedents": "IF",
                "consequents": "THEN",
                "support": "Support",
                "confidence_percent": "Confidence (%)",
                "lift": "Lift"
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No association rules available.")
else:
    st.info(
        "Run src/association_rules.py to generate association rules."
    )

# Raw filtered records
with st.expander("View Dataset Records"):
    st.dataframe(filtered, use_container_width=True)

# Download option
csv_data = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Filtered Dataset",
    data=csv_data,
    file_name="filtered_ridership_data.csv",
    mime="text/csv"
)

st.caption(
    "Academic demonstration using a sample dataset. "
    "Results represent sample records, not verified city-wide ridership."
)
