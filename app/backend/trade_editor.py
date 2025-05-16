import streamlit as st
import pandas as pd
from data_handler import save_data
from price_fetcher import get_current_price
from utils import check_price_alerts
from config import DATA_PATH

def display_trades_section(filtered_df, df):
    st.subheader("📄 Filtered Trades")

    for idx, row in filtered_df.iterrows():
        index_in_df = row.name
        with st.expander(f"📘 {row['Date'].strftime('%Y-%m-%d')} | {row['Stock']} | {row['Status']}"):
            cols = st.columns(6)
            cols[0].markdown(f"**Entry Price:** ₹{row['Entry Price']}")
            cols[1].markdown(f"**Current:** {row['Current (Change%)']}")

            for i, label in enumerate(["Target 1", "Target 2", "Target 3", "Stop Loss"]):
                cols[i+2].markdown(f"**{label}:** {row.get(label, '')}")

            if row["Status"] == "Open":
                current_price = get_current_price(row["Stock"])
                if current_price is not None:
                    alerts = check_price_alerts(
                        current_price,
                        row.get("Target 1"),
                        row.get("Target 2"),
                        row.get("Target 3"),
                        row.get("Stop Loss")
                    )
                    for alert in alerts:
                        st.warning(alert)

            if st.button("✏️ Edit", key=f"edit_{index_in_df}"):
                st.session_state.edit_index = index_in_df
                st.session_state.show_form = False
                st.rerun()

            if "edit_index" in st.session_state and st.session_state.edit_index == index_in_df:
                st.markdown("### ✏️ Edit Trade")
                with st.form(f"edit_trade_form_{index_in_df}"):
                    col1, col2, col3 = st.columns(3)
                    date = col1.date_input("Date", value=pd.to_datetime(row["Date"]))
                    stock = col2.text_input("Stock", value=row["Stock"])
                    entry_price = col3.number_input("Entry Price", value=float(row["Entry Price"]), step=0.01)

                    col4, col5, col6 = st.columns(3)
                    target1 = col4.number_input("Target 1", value=float(row.get("Target 1", 0)), step=0.01)
                    target2 = col5.number_input("Target 2", value=float(row.get("Target 2", 0)), step=0.01)
                    target3 = col6.number_input("Target 3", value=float(row.get("Target 3", 0)), step=0.01)

                    col7, col8, col9 = st.columns(3)
                    stop_loss = col7.number_input("Stop Loss", value=float(row.get("Stop Loss", 0)), step=0.01)
                    quantity = col8.number_input("Quantity", value=int(row.get("Quantity", 1)), min_value=1)
                    status = col9.selectbox("Status", ["Open", "Closed"], index=["Open", "Closed"].index(row["Status"]))

                    exit_price = st.number_input("Exit Price", value=float(row.get("Exit Price", 0)), step=0.01)
                    notes = st.text_area("Notes", value=row.get("Notes", ""))

                    save = st.form_submit_button("💾 Save Changes")
                    cancel = st.form_submit_button("❌ Cancel")

                    if save:
                        df.loc[index_in_df] = {
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
                        save_data(df, DATA_PATH)
                        st.success("✅ Trade updated successfully!")
                        del st.session_state.edit_index
                        st.rerun()

                    if cancel:
                        del st.session_state.edit_index
                        st.info("✏️ Edit cancelled.")

def new_trade_form(df):
    st.markdown("### ➕ Add a New Trade")

    if "show_form" not in st.session_state:
        st.session_state.show_form = False

    if st.button("Add New Trade"):
        st.session_state.show_form = not st.session_state.show_form

    if st.session_state.show_form:
        with st.form("trade_form"):
            col1, col2, col3 = st.columns(3)
            date = col1.date_input("Date")
            stock = col2.text_input("Stock Symbol").upper()
            entry_price = col3.number_input("Entry Price", step=0.01)

            col4, col5, col6 = st.columns(3)
            target1 = col4.number_input("Target 1", step=0.01)
            target2 = col5.number_input("Target 2", step=0.01)
            target3 = col6.number_input("Target 3", step=0.01)

            col7, col8, col9 = st.columns(3)
            stop_loss = col7.number_input("Stop Loss", step=0.01)
            quantity = col8.number_input("Quantity", value=1, min_value=1)
            status = col9.selectbox("Status", ["Open", "Closed"])

            exit_price = st.number_input("Exit Price", step=0.01)
            notes = st.text_area("Notes")

            submitted = st.form_submit_button("💾 Save Trade")

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
                df = df.append(new_trade, ignore_index=True)
                save_data(df, DATA_PATH)
                st.success("✅ Trade added!")
                st.session_state.show_form = False
