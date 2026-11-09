
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="TransitIQ | Ridership Analytics",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- CUSTOM DESIGN ----------
st.markdown("""
<style>
.stApp {
    background-color: #F4F7FB;
}
[data-testid="stHeader"] {
    background-color: rgba(244,247,251,0.9);
}
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}
.hero {
    background: linear-gradient(120deg, #102A43, #176B87);
    padding: 30px;
    border-radius: 18px;
    color: white;
    margin-bottom: 24px;
}
.hero h1 {
    color: white;
    font-size: 32px;
    margin-bottom: 8px;
}
.hero p {
    color: #D9EAF4;
    font-size: 16px;
    margin-bottom: 0;
}
.section-title {
    color: #17324D;
    font-size: 21px;
    font-weight: 700;
    margin: 15px 0;
}
[data-testid="stMetric"] {
    background: white;
    border: 1px solid #E0E7EF;
    padding: 18px;
    border-radius: 14px;
    box-shadow: 0 3px 10px rgba(20,50,80,0.04);
}
[data-testid="stMetricLabel"] {
    color: #52677D;
}
[data-testid="stMetricValue"] {
    color: #123B5D;
}
div[data-testid="stPlotlyChart"] {
    background: white;
    padding: 10px;
    border-radius: 14px;
    border: 1px solid #E0E7EF;
}
section[data-testid="stSidebar"] {
    background-color: #EAF0F7;
}
.stDownloadButton button {
    background-color: #176B87;
    color: white;
    border-radius: 9px;
}
</style>
""", unsafe_allow_html=True)

# ---------- LOAD DATA ----------
DATA = Path("data/BUS_DATA_FEB_2018.csv")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA)
    df["Ride_start_date"] = pd.to_datetime(
        df["Ride_start_date"],
        dayfirst=True,
        errors="coerce"
    )
    return df

st.markdown("""
<div class="hero">
    <h1>🚌 TransitIQ</h1>
    <p>Public Transport Ridership Analytics</p>
    <p>Explore travel patterns, busy stops and bus service usage.</p>
</div>
""", unsafe_allow_html=True)

if not DATA.exists():
    st.error("Dataset not found. Check data/BUS_DATA_FEB_2018.csv")
    st.stop()

df = load_data()
valid_dates = df["Ride_start_date"].dropna()

if valid_dates.empty:
    st.error("No valid dates found in the dataset.")
    st.stop()

# ---------- SIDEBAR ----------
st.sidebar.title("⚙️ Dashboard Controls")
st.sidebar.caption("Customize your analysis")

min_date = valid_dates.min().date()
max_date = valid_dates.max().date()

date_range = st.sidebar.date_input(
    "📅 Travel date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(date_range, (tuple, list)):
    if len(date_range) == 2:
        start_date, end_date = date_range
    elif len(date_range) == 1:
        start_date = end_date = date_range[0]
    else:
        start_date, end_date = min_date, max_date
else:
    start_date = end_date = date_range

filtered = df[
    (df["Ride_start_date"].dt.date >= start_date) &
    (df["Ride_start_date"].dt.date <= end_date)
].copy()

all_modes = sorted(
    filtered["Travel_Mode"].dropna().unique().tolist()
)

selected_modes = st.sidebar.multiselect(
    "🚌 Travel mode",
    options=all_modes,
    default=all_modes
)

if selected_modes:
    filtered = filtered[
        filtered["Travel_Mode"].isin(selected_modes)
    ]
else:
    filtered = filtered.iloc[0:0]

st.sidebar.divider()
st.sidebar.info(
    "Dataset: February 2018\n\n"
    "Source: BUS_DATA_FEB_2018.csv"
)

# ---------- KPI CARDS ----------
st.markdown(
    '<div class="section-title">📊 Key Performance Indicators</div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Rides", f"{len(filtered):,}")
c2.metric("Unique Cards", f"{filtered['Card_Number'].nunique():,}")
c3.metric(
    "Bus Services",
    f"{filtered['Bus_Service_Number'].nunique():,}"
)
c4.metric(
    "Boarding Stops",
    f"{filtered['Boarding_stop_stn'].nunique():,}"
)

st.caption(
    f"Showing data from {start_date} to {end_date}"
)
st.divider()

# ---------- CHARTS ----------
if filtered.empty:
    st.warning("No rides found for the selected filters.")
    st.stop()

st.markdown(
    '<div class="section-title">📈 Ridership Trends</div>',
    unsafe_allow_html=True
)

daily = (
    filtered.groupby(filtered["Ride_start_date"].dt.date)
    .size()
    .reset_index(name="Total Rides")
)
daily.columns = ["Date", "Total Rides"]

fig = px.area(
    daily,
    x="Date",
    y="Total Rides",
    markers=True,
    title="Daily Ridership Trend",
    color_discrete_sequence=["#176B87"]
)
fig.update_layout(
    template="plotly_white",
    margin=dict(l=20, r=20, t=55, b=20),
    hovermode="x unified"
)
st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)

with left:
    st.markdown("#### 🚏 Most Popular Boarding Stops")
    board = (
        filtered["Boarding_stop_stn"]
        .value_counts()
        .head(10)
        .sort_values()
        .rename_axis("Boarding Stop")
        .reset_index(name="Rides")
    )
    fig = px.bar(
        board,
        x="Rides",
        y="Boarding Stop",
        orientation="h",
        color_discrete_sequence=["#2589A6"]
    )
    fig.update_layout(
        template="plotly_white",
        showlegend=False,
        margin=dict(l=10, r=10, t=20, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown("#### 🏁 Most Popular Alighting Stops")
    alight = (
        filtered["Alighting_stop_stn"]
        .value_counts()
        .head(10)
        .sort_values()
        .rename_axis("Alighting Stop")
        .reset_index(name="Rides")
    )
    fig = px.bar(
        alight,
        x="Rides",
        y="Alighting Stop",
        orientation="h",
        color_discrete_sequence=["#6478D3"]
    )
    fig.update_layout(
        template="plotly_white",
        showlegend=False,
        margin=dict(l=10, r=10, t=20, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)

with left:
    st.markdown("#### 🚌 Travel Mode Distribution")
    mode = (
        filtered["Travel_Mode"]
        .value_counts()
        .rename_axis("Travel Mode")
        .reset_index(name="Rides")
    )
    fig = px.pie(
        mode,
        names="Travel Mode",
        values="Rides",
        hole=0.55,
        color_discrete_sequence=[
            "#176B87", "#55A6A0", "#F2B66D", "#6478D3"
        ]
    )
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=10, r=10, t=20, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown("#### 🎫 Card Type Distribution")
    card = (
        filtered["Card_Type"]
        .value_counts()
        .rename_axis("Card Type")
        .reset_index(name="Rides")
    )
    fig = px.bar(
        card,
        x="Card Type",
        y="Rides",
        color_discrete_sequence=["#D99A45"]
    )
    fig.update_layout(
        template="plotly_white",
        showlegend=False,
        margin=dict(l=10, r=10, t=20, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------- BUS SERVICE TABLE ----------
st.markdown(
    '<div class="section-title">🛣️ Bus Service Performance</div>',
    unsafe_allow_html=True
)

services = (
    filtered["Bus_Service_Number"]
    .value_counts()
    .head(10)
    .rename_axis("Bus Service")
    .reset_index(name="Total Rides")
)
st.dataframe(services, use_container_width=True, hide_index=True)

# ---------- DATA EXPLORER ----------
with st.expander("🔎 Explore Raw Data"):
    st.caption("Preview of up to 1,000 filtered records")
    st.dataframe(
        filtered.head(1000),
        use_container_width=True,
        hide_index=True
    )

st.download_button(
    "⬇️ Download Filtered Data (CSV)",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_ridership.csv",
    mime="text/csv"
)

st.divider()
st.caption(
    "TransitIQ | Public Transport Ridership Analytics | "
    "Data source: February 2018 dataset"
)

