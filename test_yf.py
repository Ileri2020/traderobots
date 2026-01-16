import os
import sys
from pathlib import Path
import pandas as pd
import yfinance as yf
import requests
from datetime import datetime, timedelta

# Mocking parts of HistoricalDataService to test fetch_yfinance independently
def fetch_yfinance_mock(symbol, timeframe, lookback_months):
    """Hardened YFinance fetcher."""
    yf_symbol = f"{symbol}=X" if len(symbol) == 6 else symbol
    if 'BTC' in symbol: yf_symbol = 'BTC-USD'
    if 'GOLD' in symbol or 'XAU' in symbol: yf_symbol = 'GC=F'

    interval_map = {
        'M1': '1m', 'M5': '5m', 'M15': '15m', 
        'H1': '1h', 'H4': '4h', 'D1': '1d'
    }
    interval = interval_map.get(timeframe, '1d')

    print(f"DEBUG: yf_symbol: {yf_symbol}, interval: {interval}")

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    })

    end = datetime.utcnow()
    start = end - timedelta(days=lookback_months * 30)

    print(f"DEBUG: Downloading {yf_symbol} from {start} to {end}...")

    df = yf.download(
        yf_symbol, start=start, end=end, interval=interval,
        progress=True, threads=False, session=session, auto_adjust=False
    )

    if df is None or df.empty:
        print("DEBUG: Download empty. Trying Ticker.history with period fallback...")
        ticker = yf.Ticker(yf_symbol, session=session)
        df = ticker.history(period=f"{lookback_months}mo", interval=interval)

    if df is None or df.empty:
        print(f"ERROR: YFinance returned no data for {yf_symbol}")
        return None

    print(f"DEBUG: Columns before cleanup: {df.columns}")

    # Flatten MultiIndex if exists
    if isinstance(df.columns, pd.MultiIndex):
        print("DEBUG: Flattening MultiIndex...")
        df.columns = df.columns.get_level_values(1)

    df = df.reset_index()
    
    map_cols = {
        "Date": "time", "Datetime": "time", "timestamp": "time",
        "Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "tick_volume"
    }
    df.rename(columns=map_cols, inplace=True, errors='ignore')
    
    df.columns = [c.lower() for c in df.columns]

    print(f"DEBUG: Columns after cleanup: {df.columns}")

    required = {'open', 'high', 'low', 'close', 'time'}
    if not required.issubset(set(df.columns)):
        missing = required - set(df.columns)
        print(f"ERROR: Missing columns: {missing}")
        return None

    df['time'] = pd.to_datetime(df['time'])
    if df['time'].dt.tz is not None:
        df['time'] = df['time'].dt.tz_localize(None)

    return df

if __name__ == "__main__":
    res = fetch_yfinance_mock("EURUSD", "H1", 3)
    if res is not None:
        print(f"Success! Rows: {len(res)}")
        print(res.head())
    else:
        print("Fetch failed.")
