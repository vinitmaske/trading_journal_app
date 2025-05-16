import sys
import os

# Add current app folder to sys.path for internal imports
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import streamlit as st
from datetime import datetime
import pandas as pd

from config import DATA_PATH, REFRESH_INTERVAL
from backend.data_handler import load_trades
from services.price_fetcher import get_current_price
from backend.pnl_calculator import compute_pnl_summary
from utils.trade_filters import apply_filters
from backend.trade_editor import display_trades_section, new_trade_form



# --- Load Data ---
df = load_data(DATA_PATH)

# --- Streamlit UI ---
st.set_page_config(page_title="Trading Journal", layout="wide")
st.title("📘 Personal Trading Journal")

# --- Auto-refresh logic ---
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = datetime.now()

st.markdown(f"⏱️ Auto-refreshing every **{REFRESH_INTERVAL} seconds**")
if (datetime.now() - st.session_state.last_refresh).seconds > REFRESH_INTERVAL:
    st.session_state.last_refresh = datetime.now()
    st.rerun()

# --- Update Live Prices ---
df = update_current_prices(df)

# --- PnL Summary ---
open_pnl, closed_pnl, total_pnl = compute_pnl_summary(df)
st.subheader("💰 Total PnL Summary")
st.write(f"🔓 Open PnL: ₹{open_pnl:,.2f} | ✅ Closed PnL: ₹{closed_pnl:,.2f} | 🧾 Total PnL: ₹{total_pnl:,.2f}")

# --- Filters ---
st.markdown("### 🔍 Filter Trades")
start_date, end_date, stock_filter, status_filter = apply_filters(df)

# --- Filtered Data ---
filtered_df = df.copy()
if not df.empty:
    filtered_df = filtered_df[
        (filtered_df["Date"] >= pd.to_datetime(start_date)) &
        (filtered_df["Date"] <= pd.to_datetime(end_date))
    ]
    if stock_filter:
        filtered_df = filtered_df[filtered_df["Stock"].str.upper().str.contains(stock_filter)]
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df["Status"] == status_filter]

# --- Trade Viewer + Editor ---
display_trades_section(filtered_df, df)

# --- Add New Trade ---
new_trade_form(df)
