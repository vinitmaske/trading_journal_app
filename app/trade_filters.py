import pandas as pd

def apply_filters(df, start_date, end_date, stock_filter, status_filter):
    filtered_df = df.copy()
    if not df.empty:
        filtered_df = filtered_df[
            (filtered_df["Date"] >= pd.to_datetime(start_date)) &
            (filtered_df["Date"] <= pd.to_datetime(end_date))
        ]
        if stock_filter:
            filtered_df = filtered_df[filtered_df["Stock"].str.upper().str.contains(stock_filter.upper())]
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df["Status"] == status_filter]
    return filtered_df
