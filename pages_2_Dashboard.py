import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

# -------------------- Page setup --------------------
st.set_page_config(page_title="NYC Flights — Dashboard", page_icon="📊", layout="wide")
st.title("📊 NYC Flights — Interactive Dashboard")

# -------------------- Data loading --------------------
DATA_PATH = Path(r"Flights export 2025.csv")  # عدّلي المسار لو لزم
if not DATA_PATH.exists():
    st.error(f"CSV not found at: {DATA_PATH.resolve()}")
    st.stop()

@st.cache_data(show_spinner=False)
def load_df(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    rename_map = {
        "dayofmonth": "day", "day_of_month": "day",
        "arrdelay": "arr_delay", "depdelay": "dep_delay",
        "carriername": "carrier", "carrier_name": "carrier",
        "origin_airport": "origin", "dest_airport": "dest",
        "originairportid": "origin", "destairportid": "dest",
    }
    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)
    for c in ["year","month","day","hour","minute","arr_delay","dep_delay","distance","air_time"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

df_main = load_df(DATA_PATH)
palette = px.colors.qualitative.Set2

# -------------------- Helpers --------------------
def apply_filters(d: pd.DataFrame, months_sel, days_sel, extra_filter):
    if not isinstance(d, pd.DataFrame):
        st.error(f"Internal error: expected DataFrame, got {type(d).__name__}.")
        st.stop()
    out = d.copy()
    if "month" in out.columns and months_sel:
        out = out[out["month"].isin(months_sel)]
    if "day" in out.columns and days_sel:
        out = out[out["day"].isin(days_sel)]
    if extra_filter is not None:
        col, vals = extra_filter
        if col in out.columns and vals:
            out = out[out[col].astype(str).isin([str(v) for v in vals])]
    return out

months_all = sorted(df_main["month"].dropna().unique()) if "month" in df_main else []
days_all   = sorted(df_main["day"].dropna().unique())   if "day"   in df_main else []
car_all    = sorted(df_main["carrier"].dropna().unique()) if "carrier" in df_main else []
org_all    = sorted(df_main["origin"].dropna().unique())  if "origin"  in df_main else []

# ==================== Chart 1 ====================
st.subheader("Q1) Which carriers have higher arrival delays?")
fc1a, fc1b, fc1c = st.columns(3)
m1 = fc1a.multiselect("Filter: Months", months_all, default=months_all, key="c1_months") if months_all else []
d1 = fc1b.multiselect("Filter: Days",   days_all,   default=days_all,   key="c1_days")   if days_all   else []
c1 = fc1c.multiselect("Filter: Carrier", car_all,   default=car_all,   key="c1_car")    if car_all    else []
dff1 = apply_filters(df_main, m1, d1, ("carrier", c1) if c1 else None)

if {"carrier","arr_delay"}.issubset(dff1.columns) and len(dff1):
    fig1 = px.box(
        dff1, x="carrier", y="arr_delay", points="outliers",
        labels={"carrier": "Carrier", "arr_delay": "Arrival delay (min)"},
        color="carrier", color_discrete_sequence=palette,
        title="Arrival delay by carrier"
    )
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.info("Required columns not found: carrier, arr_delay")

st.markdown("---")

# ==================== Chart 2 ====================
st.subheader("Q2) When (hour) do departures face the most delay?")
fc2a, fc2b, fc2c = st.columns(3)
m2 = fc2a.multiselect("Filter: Months", months_all, default=months_all, key="c2_months") if months_all else []
d2 = fc2b.multiselect("Filter: Days",   days_all,   default=days_all,   key="c2_days")   if days_all   else []
o2 = fc2c.multiselect("Filter: Origin", org_all,    default=org_all,    key="c2_org")    if org_all    else []
dff2 = apply_filters(df_main, m2, d2, ("origin", o2) if o2 else None)

if {"hour","dep_delay"}.issubset(dff2.columns) and len(dff2):
    g2 = dff2.groupby("hour", as_index=False)["dep_delay"].mean()
    fig2 = px.line(
        g2, x="hour", y="dep_delay", markers=True,
        labels={"hour": "Hour of day (0–23)", "dep_delay": "Avg departure delay (min)"},
        title="Average departure delay by hour"
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Required columns not found: hour, dep_delay")

st.markdown("---")

# ==================== Chart 3 ====================
st.subheader("Q3) What is the distribution of flight distances?")
fc3a, fc3b = st.columns(2)
m3 = fc3a.multiselect("Filter: Months", months_all, default=months_all, key="c3_months") if months_all else []
d3 = fc3b.multiselect("Filter: Days",   days_all,   default=days_all,   key="c3_days")   if days_all   else []
dff3 = apply_filters(df_main, m3, d3, None)

if "distance" in dff3.columns and len(dff3):
    fig3 = px.histogram(
        dff3, x="distance", nbins=60,
        labels={"distance": "Distance (miles)"},
        title="Distribution of distance (miles)"
    )
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("Required column not found: distance")

st.markdown("---")

# ==================== Chart 4 ====================
st.subheader("Q4) How does distance relate to arrival delay?")
fc4a, fc4b, fc4c = st.columns(3)
m4 = fc4a.multiselect("Filter: Months", months_all, default=months_all, key="c4_months") if months_all else []
d4 = fc4b.multiselect("Filter: Days",   days_all,   default=days_all,   key="c4_days")   if days_all   else []
c4 = fc4c.multiselect("Filter: Carrier", car_all,   default=car_all,   key="c4_car")    if car_all    else []
dff4 = apply_filters(df_main, m4, d4, ("carrier", c4) if c4 else None)

if {"distance","arr_delay"}.issubset(dff4.columns) and len(dff4):
    color_series = dff4["carrier"].astype(str) if "carrier" in dff4.columns else None
    fig4 = px.scatter(
        dff4, x="distance", y="arr_delay", color=color_series, opacity=0.6,
        labels={"distance": "Distance (miles)", "arr_delay": "Arrival delay (min)", "color": "Carrier"},
        title="Arrival delay vs distance",
        color_discrete_sequence=palette
    )
    st.plotly_chart(fig4, use_container_width=True)
else:
    st.info("Required columns not found: distance, arr_delay")

st.markdown("---")

# ==================== Chart 5 ====================
st.subheader("Q5) Which months have the highest late-arrival rate?")
fc5a, fc5b, fc5c = st.columns(3)
m5 = fc5a.multiselect("Filter: Months", months_all, default=months_all, key="c5_months") if months_all else []
d5 = fc5b.multiselect("Filter: Days",   days_all,   default=days_all,   key="c5_days")   if days_all   else []
c5 = fc5c.multiselect("Filter: Carrier", car_all,   default=car_all,   key="c5_car")    if car_all    else []
dff5 = apply_filters(df_main, m5, d5, ("carrier", c5) if c5 else None)

if {"month","arr_delay"}.issubset(dff5.columns) and len(dff5):
    g5 = dff5.assign(is_late = dff5["arr_delay"] >= 15).groupby("month", as_index=False)["is_late"].mean()
    g5["late_rate_pct"] = (g5["is_late"] * 100).round(1)
    fig5 = px.bar(
        g5, x="month", y="late_rate_pct",
        labels={"month": "Month (1–12)", "late_rate_pct": "Late rate (%)"},
        title="Late-arrival rate by month (%)",
        color_discrete_sequence=palette
    )
    st.plotly_chart(fig5, use_container_width=True)
else:
    st.info("Required columns not found: month, arr_delay")
