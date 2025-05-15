import streamlit as st
import pandas as pd
import os
import yfinance as yf
from datetime import datetime

# --- CONFIGURATION ---
REFRESH_INTERVAL = 60  # seconds
DATA_PATH = os.path.join("..", "data", "trades.csv")

# --- Cached Price Fetching ---
@st.cache_data(ttl=300)
def get_current_price(stock_symbol):
    try:
        ticker = yf.Ticker(stock_symbol + ".NS")
        data = ticker.history(period="1d")
        if not data.empty:
            return data['Close'].iloc[-1]
    except:
        return None
    return None

# --- Load or Initialize CSV ---
if os.path.exists(DATA_PATH):
    df = pd.read_csv(DATA_PATH)
else:
    df = pd.DataFrame(columns=[
        "Date", "Stock", "Entry Price", "Target 1", "Target 2", "Target 3", "Stop Loss",
        "Quantity", "Status", "Exit Price", "Notes"
    ])
    df.to_csv(DATA_PATH, index=False)

st.set_page_config(page_title="Trading Journal", layout="wide")
st.title("📘 Personal Trading Journal")

# --- Auto Refresh ---
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = datetime.now()

st.markdown(f"⏱️ Auto-refreshing every **{REFRESH_INTERVAL} seconds**")
if (datetime.now() - st.session_state.last_refresh).seconds > REFRESH_INTERVAL:
    st.session_state.last_refresh = datetime.now()
    st.rerun()

# --- Data Preprocessing ---
if not df.empty:
    df["Date"] = pd.to_datetime(df["Date"])
    current_with_pct = []
    for _, trade in df.iterrows():
        if trade["Status"] == "Open":
            price = get_current_price(trade["Stock"])
            if price is not None:
                pct_change = ((price - trade["Entry Price"]) / trade["Entry Price"]) * 100
                current_with_pct.append(f"{price:.2f} ({pct_change:+.2f}%)")
            else:
                current_with_pct.append("Price N/A")
        else:
            current_with_pct.append("Closed")
    df["Current (Change%)"] = current_with_pct

# --- PnL Summary ---
def compute_pnl_summary(df):
    open_pnl = 0
    closed_pnl = 0
    for _, row in df.iterrows():
        if row["Status"] == "Open":
            price = get_current_price(row["Stock"])
            if price is not None:
                open_pnl += (price - row["Entry Price"]) * row["Quantity"]
        elif row["Status"] == "Closed":
            closed_pnl += (row["Exit Price"] - row["Entry Price"]) * row["Quantity"]
    return open_pnl, closed_pnl, open_pnl + closed_pnl

open_pnl, closed_pnl, total_pnl = compute_pnl_summary(df)
st.subheader("💰 Total PnL Summary")
st.write(f"🔓 Open PnL: ₹{open_pnl:,.2f} | ✅ Closed PnL: ₹{closed_pnl:,.2f} | 🧾 Total PnL: ₹{total_pnl:,.2f}")

# --- Filters ---
st.markdown("### 🔍 Filter Trades")
col1, col2, col3 = st.columns(3)
start_date = col1.date_input("From Date", value=df["Date"].min() if not df.empty else pd.to_datetime("today"))
end_date = col2.date_input("To Date", value=df["Date"].max() if not df.empty else pd.to_datetime("today"))
stock_filter = col3.text_input("Stock Symbol Filter (optional)").upper()
status_filter = st.radio("Filter by Status:", ["All", "Open", "Closed"], horizontal=True)

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

# --- Display Trades with Edit Button ---
st.subheader("📄 Filtered Trades")

for idx, row in filtered_df.iterrows():
    index_in_df = df[(df["Date"] == row["Date"]) & (df["Stock"] == row["Stock"])].index[0]
    with st.expander(f"📘 {row['Date'].strftime('%Y-%m-%d')} | {row['Stock']} | {row['Status']}"):
        cols = st.columns(6)
        cols[0].markdown(f"**Entry Price:** ₹{row['Entry Price']}")
        cols[1].markdown(f"**Current:** {row['Current (Change%)']}")
        cols[2].markdown(f"**T1:** {row.get('Target 1', '')}")
        cols[3].markdown(f"**T2:** {row.get('Target 2', '')}")
        cols[4].markdown(f"**T3:** {row.get('Target 3', '')}")
        cols[5].markdown(f"**SL:** {row.get('Stop Loss', '')}")

        if st.button("✏️ Edit", key=f"edit_{index_in_df}"):
            st.session_state.edit_index = index_in_df

# --- Inline Edit Form ---
if "edit_index" in st.session_state:
    i = st.session_state.edit_index
    edit_row = df.loc[i]

    st.markdown("### ✏️ Edit Trade")

    with st.form("edit_trade_form"):
        col1, col2, col3 = st.columns(3)
        date = col1.date_input("Date", value=pd.to_datetime(edit_row["Date"]))
        stock = col2.text_input("Stock", value=edit_row["Stock"])
        entry_price = col3.number_input("Entry Price", value=float(edit_row["Entry Price"]), step=0.01)

        col4, col5, col6 = st.columns(3)
        target1 = col4.number_input("Target 1", value=float(edit_row.get("Target 1", 0)), step=0.01)
        target2 = col5.number_input("Target 2", value=float(edit_row.get("Target 2", 0)), step=0.01)
        target3 = col6.number_input("Target 3", value=float(edit_row.get("Target 3", 0)), step=0.01)

        col7, col8, col9 = st.columns(3)
        stop_loss = col7.number_input("Stop Loss", value=float(edit_row.get("Stop Loss", 0)), step=0.01)
        quantity = col8.number_input("Quantity", value=int(edit_row.get("Quantity", 1)), min_value=1)
        status = col9.selectbox("Status", ["Open", "Closed"], index=["Open", "Closed"].index(edit_row["Status"]))

        exit_price = st.number_input("Exit Price", value=float(edit_row.get("Exit Price", 0)), step=0.01)
        notes = st.text_area("Notes", value=edit_row.get("Notes", ""))

        save = st.form_submit_button("💾 Save Changes")
        cancel = st.form_submit_button("❌ Cancel")

        if save:
            df.loc[i] = {
                "Date": date,
                "Stock": stock,
                "Entry Price": entry_price,
                "Target 1": target1,
                "Target 2": target2,
                "Target 3": target3,
                "Stop Loss": stop_loss,
                "Quantity": quantity,
                "Status": status,
                "Exit Price": exit_price,
                "Notes": notes
            }
            df.to_csv(DATA_PATH, index=False)
            st.success("✅ Trade updated successfully!")
            del st.session_state.edit_index
            st.experimental_rerun()

        if cancel:
            del st.session_state.edit_index
            st.info("✏️ Edit cancelled.")

# --- Add New Trade ---
st.markdown("### ➕ Add a New Trade")

if "show_form" not in st.session_state:
    st.session_state.show_form = False

if st.button("Add New Trade"):
    st.session_state.show_form = not st.session_state.show_form

if st.session_state.show_form:
    with st.form("trade_form"):
        col1, col2, col3 = st.columns(3)
        date = col1.date_input("Date", value=pd.to_datetime("today"))
        stock = col2.text_input("Stock")
        entry_price = col3.number_input("Entry Price", step=0.01)

        col4, col5, col6 = st.columns(3)
        target1 = col4.number_input("Target 1 (optional)", step=0.01)
        target2 = col5.number_input("Target 2 (optional)", step=0.01)
        target3 = col6.number_input("Target 3 (optional)", step=0.01)

        col7, col8, col9 = st.columns(3)
        stop_loss = col7.number_input("Stop Loss", step=0.01)
        quantity = col8.number_input("Quantity", min_value=1)
        status = col9.selectbox("Status", ["Open", "Closed"])

        exit_price = st.number_input("Exit Price (if closed)", step=0.01)
        notes = st.text_area("Notes")

        submitted = st.form_submit_button("Submit Trade")

        if submitted:
            new_trade = {
                "Date": date,
                "Stock": stock,
                "Entry Price": entry_price,
                "Target 1": target1,
                "Target 2": target2,
                "Target 3": target3,
                "Stop Loss": stop_loss,
                "Quantity": quantity,
                "Status": status,
                "Exit Price": exit_price,
                "Notes": notes
            }
            df = pd.concat([df, pd.DataFrame([new_trade])], ignore_index=True)
            df.to_csv(DATA_PATH, index=False)
            st.success("✅ Trade added successfully!")
            st.session_state.show_form = False
            st.experimental_rerun()
