
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Public Transport Analytics",
    page_icon="🚌",
    layout="wide"
)

st.title("🚌 Public Transport Ridership Analytics")
st.markdown("### February 2018 | Interactive Data Dashboard")

DATA = Path("data/BUS_DATA_FEB_2018.csv")
RESULTS = Path("results")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA)
    df["Ride_start_date"] = pd.to_datetime(
        df["Ride_start_date"], dayfirst=True, errors="coerce"
    )
    return df

@st.cache_data
def load_result(filename):
    return pd.read_csv(RESULTS / filename)

if not DATA.exists():
    st.error("Source CSV file not found in the data folder.")
    st.stop()

df = load_data()
daily = load_result("daily_ridership.csv")
travel = load_result("travel_mode_analysis.csv")
boarding = load_result("top_boarding_stops.csv")
alighting = load_result("top_alighting_stops.csv")
services = load_result("top_bus_services.csv")
cards = load_result("card_type_analysis.csv")

# Sidebar filters
st.sidebar.header("Dashboard Filters")

valid_dates = df["Ride_start_date"].dropna()

if valid_dates.empty:
    st.error("No valid ride dates found.")
    st.stop()

min_date = valid_dates.min().date()
max_date = valid_dates.max().date()

date_range = st.sidebar.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range

filtered = df[
    (df["Ride_start_date"].dt.date >= start_date) &
    (df["Ride_start_date"].dt.date <= end_date)
].copy()

modes = sorted(filtered["Travel_Mode"].dropna().unique().tolist())
selected_modes = st.sidebar.multiselect(
    "Travel mode",
    modes,
    default=modes
)

if selected_modes:
    filtered = filtered[filtered["Travel_Mode"].isin(selected_modes)]
else:
    filtered = filtered.iloc[0:0]

# KPI cards
c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Rides", f"{len(filtered):,}")
c2.metric("Unique Cards", f"{filtered['Card_Number'].nunique():,}")
c3.metric("Bus Services", f"{filtered['Bus_Service_Number'].nunique():,}")
c4.metric("Boarding Stops", f"{filtered['Boarding_stop_stn'].nunique():,}")

st.divider()

# Charts based on selected filters
st.subheader("📈 Daily Ridership Trend")

if not filtered.empty:
    daily_filtered = (
        filtered.groupby(filtered["Ride_start_date"].dt.date)
        .size()
        .reset_index(name="Total Rides")
    )
    daily_filtered.columns = ["Date", "Total Rides"]

    fig = px.line(
        daily_filtered,
        x="Date",
        y="Total Rides",
        markers=True,
        title="Rides per Day"
    )
    st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)

    with left:
        st.subheader("🚏 Top Boarding Stops")
        top_board = filtered["Boarding_stop_stn"].value_counts().head(10)
        chart = top_board.rename_axis("Stop").reset_index(name="Rides")
        st.plotly_chart(
            px.bar(chart, x="Rides", y="Stop", orientation="h"),
            use_container_width=True
        )

    with right:
        st.subheader("🏁 Top Alighting Stops")
        top_alight = filtered["Alighting_stop_stn"].value_counts().head(10)
        chart = top_alight.rename_axis("Stop").reset_index(name="Rides")
        st.plotly_chart(
            px.bar(chart, x="Rides", y="Stop", orientation="h"),
            use_container_width=True
        )

    left, right = st.columns(2)

    with left:
        st.subheader("🚌 Travel Mode Distribution")
        mode_data = filtered["Travel_Mode"].value_counts()
        mode_chart = mode_data.rename_axis("Travel Mode").reset_index(name="Rides")
        st.plotly_chart(
            px.pie(mode_chart, names="Travel Mode", values="Rides", hole=0.4),
            use_container_width=True
        )

    with right:
        st.subheader("🎫 Card Type Distribution")
        card_data = filtered["Card_Type"].value_counts()
        card_chart = card_data.rename_axis("Card Type").reset_index(name="Rides")
        st.plotly_chart(
            px.bar(card_chart, x="Card Type", y="Rides"),
            use_container_width=True
        )

    st.subheader("🛣️ Top Bus Services")
    service_data = (
        filtered["Bus_Service_Number"].value_counts()
        .head(10).rename_axis("Bus Service")
        .reset_index(name="Rides")
    )
    st.plotly_chart(
        px.bar(service_data, x="Bus Service", y="Rides"),
        use_container_width=True
    )

    with st.expander("View filtered raw data"):
        st.dataframe(filtered.head(1000), use_container_width=True)

    st.download_button(
        "Download filtered data as CSV",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="filtered_ridership.csv",
        mime="text/csv"
    )
else:
    st.warning("No rides match the selected filters.")

st.caption("Data source: BUS_DATA_FEB_2018.csv")
