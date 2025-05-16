import pandas as pd

def check_price_alerts(current_price, t1, t2, t3, sl):
    alerts = []
    threshold_pct = 2  # %

    def is_near(target):
        if pd.isna(target) or target == 0:
            return False
        return abs((current_price - target) / target * 100) <= threshold_pct

    if is_near(t1): alerts.append("🎯 Near Target 1")
    if is_near(t2): alerts.append("🎯 Near Target 2")
    if is_near(t3): alerts.append("🎯 Near Target 3")
    if is_near(sl): alerts.append("⚠️ Near Stop Loss")

    return alerts
