from app.services.price_fetcher import get_current_price

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
