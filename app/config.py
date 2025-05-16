from pathlib import Path

# --- File Paths ---
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "trades.csv"  # make sure the file exists at this location

# --- Auto-refresh interval in seconds ---
REFRESH_INTERVAL = 60  # adjust as needed

# --- You can also centralize any constants here in future ---
# e.g., ALERT_THRESHOLD = 2
