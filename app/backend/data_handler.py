import pandas as pd
import os
from config import DATA_PATH
import streamlit as st  # Import Streamlit for warning (optional)

def load_trades():
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        # Parse the Date column to datetime, coerce errors to NaT
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Optionally warn about bad date rows and drop them
        if df['Date'].isnull().any():
            st.warning(f"{df['Date'].isnull().sum()} rows have invalid dates and will be ignored.")
            df = df.dropna(subset=['Date'])
    else:
        df = pd.DataFrame(columns=[
            "Date", "Stock", "Entry Price", "Target 1", "Target 2", "Target 3", "Stop Loss",
            "Quantity", "Status", "Exit Price", "Notes"
        ])
        df.to_csv(DATA_PATH, index=False)
    return df

def save_trades(df):
    # Save dates in consistent format (optional)
    df.to_csv(DATA_PATH, index=False, date_format='%Y-%m-%d')
