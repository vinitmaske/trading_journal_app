import pandas as pd
import os
from config import DATA_PATH

def load_trades():
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
    else:
        df = pd.DataFrame(columns=[
            "Date", "Stock", "Entry Price", "Target 1", "Target 2", "Target 3", "Stop Loss",
            "Quantity", "Status", "Exit Price", "Notes"
        ])
        df.to_csv(DATA_PATH, index=False)
    return df

def save_trades(df):
    df.to_csv(DATA_PATH, index=False)
