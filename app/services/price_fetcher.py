import yfinance as yf
import streamlit as st

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
