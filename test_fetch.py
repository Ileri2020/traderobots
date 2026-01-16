import os
import django
import sys
from pathlib import Path

# Setup Django
sys.path.append(str(Path(__file__).resolve().parent / "backend"))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'traderobots.settings')
django.setup()

from trading.data_service import HistoricalDataService

def test():
    symbol = "EURUSD"
    timeframe = "H1"
    lookback = 3
    
    print(f"Testing fetch for {symbol} {timeframe}...")
    try:
        df, report = HistoricalDataService.fetch_data(symbol, timeframe, lookback)
        print(f"Success! Source: {report['data_source']}, Rows: {len(df)}")
        print(df.head())
    except Exception as e:
        print(f"Failed: {str(e)}")

if __name__ == "__main__":
    test()
