import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

st.set_page_config(page_title="NYC Flights — Overview", page_icon="✈️", layout="wide")
st.title("✈️ NYC Flights — Overview & Insights")

# ✅ مصدر البيانات (Kaggle)
st.markdown(
    "Data source: **Kaggle** — "
    "[Flights (NYC 2025)](https://www.kaggle.com/datasets/mahoora00135/flights/data)"
)

st.caption("Before-departure only (no leakage) • origin→One-Hot • carrier/dest→Binary • HHMM→minutes")


DATA_PATH = Path(r"Flights export 2025.csv") 
@st.cache_data(show_spinner=False)
def load_df(path: Path) -> pd.DataFrame:
    if not path.exists():
        st.error(f"CSV not found at: {path.resolve()}")
        st.stop()
    df = pd.read_csv(path)
    # مشتقات بسيطة للعرض
    if "month" in df.columns:
        df["month_str"] = df["month"].astype(str)
    return df

df = load_df(DATA_PATH)

# لمحة سريعة
c1, c2, c3 = st.columns(3)
c1.metric("Rows", f"{len(df):,}")
c2.metric("Columns", f"{df.shape[1]}")
c3.metric("Any NaN cols", f"{df.isna().any().sum()}")

with st.expander("👀 Data preview (first 50 rows)", expanded=False):
    st.dataframe(df.head(50), use_container_width=True)

with st.expander("🧼 Missing values (%) by column", expanded=False):
    mv = (df.isna().mean()*100).round(2).sort_values(ascending=False)
    st.dataframe(mv.to_frame("missing_%"), use_container_width=True)

st.markdown("---")
st.caption("Insights & modeling use only **pre-departure** features to avoid leakage.")
