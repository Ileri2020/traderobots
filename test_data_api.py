import os
import sys
import django
from datetime import datetime, timedelta

# Patch django.utils.six for djongo
try:
    import six
except ImportError:
    # If six is not installed, we can try to install it or mock it
    import types
    six = types.ModuleType('six')
    sys.modules['six'] = six

import django.utils
django.utils.six = six
sys.modules['django.utils.six'] = six

# Setup Django environment
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'traderobots.settings')
django.setup()

from trading.data_service import HistoricalDataService
from trading.mt5_connector import MT5Connector

def test_fetch(symbol, timeframe='H1', lookback=1):
    print(f"\n--- Testing Symbol: {symbol} ---")
    try:
        # Pre-connect to MT5 for testing
        print("DEBUG: Connecting to MT5...")
        MT5Connector.connect_mt5("100690024", "R9JzFCyBFD@QZPT", "XMGlobal-MT5 5")
        
        df, info = HistoricalDataService.fetch_data(symbol, timeframe, lookback, allow_fallback=True)
        print(f"SUCCESS: {symbol} | Source: {info['data_source']} | Candles: {info['candle_count']}")
        print(df.head(2))
    except Exception as e:
        print(f"FAILED: {symbol} | Error: {str(e)}")

if __name__ == "__main__":
    symbols_to_test = ['EURUSD', 'USDJPY', 'GBPUSD', 'XAUUSD', 'BTCUSD']
    for sym in symbols_to_test:
        test_fetch(sym)
