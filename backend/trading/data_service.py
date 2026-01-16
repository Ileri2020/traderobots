import pandas as pd
import yfinance as yf
import requests
import os
import time
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from django.conf import settings
from .mt5_connector import MT5Connector

# Create a shared session for yfinance to avoid blockage
yf_session = requests.Session()
yf_session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Origin': 'https://finance.yahoo.com',
    'Referer': 'https://finance.yahoo.com/'
})

class HistoricalDataService:
    RETRIES = 3
    BACKOFF = 2  # seconds
    CACHE_TTL_MINUTES = 60

    @staticmethod
    def get_cache_path(symbol, timeframe):
        symbol = symbol.upper()
        try:
            base_dir = Path(settings.BASE_DIR)
        except:
            base_dir = Path(__file__).resolve().parent.parent

        cache_dir = base_dir / "trading_data" / "cache" / timeframe
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir / f"{symbol}.pkl"

    @staticmethod
    def save_cache(symbol, timeframe, df):
        path = HistoricalDataService.get_cache_path(symbol, timeframe)
        payload = {
            "timestamp": datetime.utcnow(),
            "data": df,
        }
        with open(path, "wb") as f:
            pickle.dump(payload, f)

    @staticmethod
    def load_cache(symbol, timeframe):
        path = HistoricalDataService.get_cache_path(symbol, timeframe)
        if not path.exists():
            return None

        try:
            with open(path, "rb") as f:
                payload = pickle.load(f)
            
            age = datetime.utcnow() - payload["timestamp"]
            if age > timedelta(minutes=HistoricalDataService.CACHE_TTL_MINUTES):
                return None
                
            return payload["data"]
        except:
            return None

    @staticmethod
    def _save_to_forex_data(df, ticker):
        """Saves data to a local folder as requested by the user."""
        try:
            folder = "forex_data"
            if not os.path.exists(folder):
                os.makedirs(folder)
            
            # Handle '=' in symbols for file names
            clean_ticker = ticker.replace("=", "_")
            filename = f"{folder}/{clean_ticker}.csv"
            df.to_csv(filename)
            print(f"DEBUG: Saved data for {ticker} to {filename}")
        except Exception as e:
            print(f"DEBUG: Error saving to forex_data: {e}")

    @staticmethod
    def fetch_yfinance(symbol, timeframe, lookback_months):
        """Ultra-resilient YFinance fetcher with local storage saving."""
        s = symbol.upper()
        
        # Test both formats: standard and user-suggested
        candidates = []
        if len(s) == 6:
            candidates.append(f"{s}=X")
            if s.startswith('USD'): candidates.append(f"{s[3:]}=X")
            if s.endswith('USD'): candidates.append(f"{s[:3]}=X")
        
        candidates.append(s)
        
        if 'BTC' in s: candidates = ['BTC-USD']
        if 'GOLD' in s or 'XAU' in s: candidates = ['GC=F']

        interval_map = {
            'M1': '1m', 'M2': '2m', 'M5': '5m', 'M15': '15m', 
            'H1': '1h', 'H4': '4h', 'D1': '1d'
        }
        requested_interval = interval_map.get(timeframe, '1h')
        
        last_error = None
        for yf_symbol in candidates:
            try:
                # Throttling/Cooldown
                time.sleep(1)
                # 1. User wants ALWAYS query in minutes to save to folder
                # We do this first (max 7 days for 1m)
                if requested_interval != '1m':
                    print(f"DEBUG: Fetching 1m data for {yf_symbol} to save to folder...")
                    m1_data = yf.download(
                        yf_symbol, 
                        period="7d", 
                        interval="1m", 
                        progress=False, 
                        threads=False,
                        auto_adjust=True,
                        session=yf_session
                    )
                    if m1_data is not None and not m1_data.empty:
                        HistoricalDataService._save_to_forex_data(m1_data, yf_symbol)

                # 2. Fetch data for the robot using requested timeframe
                print(f"DEBUG: Trying YFinance Download for {yf_symbol} at {requested_interval}...")
                df = yf.download(
                    yf_symbol, 
                    period=f"{lookback_months}mo", 
                    interval=requested_interval, 
                    progress=False, 
                    threads=False,
                    auto_adjust=True,
                    session=yf_session
                )
                
                if df is not None and not df.empty:
                    # Display first five rows as requested
                    print(f"\n--- FIRST 5 ROWS FOR {yf_symbol} ---")
                    print(df.head())
                    print("----------------------------------\n")

                    # If this was a 1m fetch and we hadn't saved it yet, save it
                    if requested_interval == '1m':
                        HistoricalDataService._save_to_forex_data(df, yf_symbol)

                    # Flatten MultiIndex if exists
                    if isinstance(df.columns, pd.MultiIndex):
                        # Modern yfinance puts 'Price' or 'Ticker' in levels. 
                        # We want the one that has OHLC.
                        if 'Open' in df.columns.get_level_values(0):
                            df.columns = df.columns.get_level_values(0)
                        elif 'Open' in df.columns.get_level_values(1):
                            df.columns = df.columns.get_level_values(1)
                        else:
                            # Fallback to level 0
                            df.columns = df.columns.get_level_values(0)

                    df = df.reset_index()
                    map_cols = {
                        "Date": "time", "Datetime": "time", "timestamp": "time",
                        "Open": "open", "High": "high", "Low": "low", "Close": "close", 
                        "Volume": "tick_volume"
                    }
                    df.rename(columns=map_cols, inplace=True, errors='ignore')
                    df.columns = [c.lower() for c in df.columns]
                    
                    required = {'open', 'high', 'low', 'close', 'time'}
                    if required.issubset(set(df.columns)):
                        df['time'] = pd.to_datetime(df['time']).dt.tz_localize(None)
                        
                        # Data Type Safety
                        for col in ['open', 'high', 'low', 'close']:
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                        
                        df.dropna(subset=['open', 'high', 'low', 'close'], inplace=True)
                        
                        if 'tick_volume' not in df.columns:
                            df['tick_volume'] = 0
                        
                        return df
                    else:
                        missing = required - set(df.columns)
                        print(f"DEBUG: Missing columns for {yf_symbol}: {missing}. Found: {list(df.columns)}")
                        last_error = f"Missing columns: {missing}"
                else:
                     last_error = "No data returned (empty DataFrame)"
                        
            except Exception as e:
                last_error = str(e)
                print(f"DEBUG: YF attempt for {yf_symbol} failed: {last_error}")

        raise RuntimeError(f"YFinance failed for all candidates {candidates}. Last error: {last_error}")


    @staticmethod
    def fetch_data(symbol, timeframe, lookback_months, allow_fallback=True, account=None):
        """Orchestrator: Cache -> MT5 -> YFinance."""
        # 1. Check Cache
        cached_df = HistoricalDataService.load_cache(symbol, timeframe)
        if cached_df is not None:
            print(f"DEBUG: Cache Hit for {symbol}")
            return cached_df, {"status": "SUCCESS", "data_source": "CACHE", "candle_count": len(cached_df)}

        errors = {}

        # 2. Try MT5
        if account:
            try:
                import MetaTrader5 as mt5
                from trading.user_mt5_manager import UserMT5Manager
                
                print(f"DEBUG: Bootstrapping MT5 for {symbol} (User {account.user.id})...")
                mt5m = UserMT5Manager(account.user.id, account)
                mt5m.connect()

                try:
                    # Logic from MT5Connector.get_market_data_range inline or helper?
                    # We can use MT5Connector.get_market_data_range BUT it must NOT try to connect again.
                    # It accepts credentials=None to skip connection.
                    end = datetime.now()
                    start = end - timedelta(days=lookback_months * 30)
                    
                    # We call get_market_data_range with credentials=None so it uses existing connection
                    df = MT5Connector.get_market_data_range(symbol, timeframe, start, end, credentials=None)
                    
                    if df is not None and not df.empty:
                        print(f"\n--- FIRST 5 ROWS FOR {symbol} (MT5) ---")
                        print(df.head())
                        print("---------------------------------------\n")
                        
                    HistoricalDataService.save_cache(symbol, timeframe, df)
                    mt5m.shutdown()
                    return df, {"status": "SUCCESS", "data_source": "MT5", "candle_count": len(df)}
                except Exception as e:
                    mt5m.shutdown()
                    raise e

            except Exception as e:
                errors["mt5"] = str(e)
                # time.sleep? Backoff might loop inside this block if we wanted retries, 
                # but UserMT5Manager connect/shutdown overhead is high for retries.
                # Assuming one good try is enough or user retry logic applies.
        else:
            errors["mt5"] = "No account provided for MT5 fetch"

        # 3. Try YFinance with Retries
        if allow_fallback:
            print(f"DEBUG: MT5 failed or skipped, falling back to YFinance for {symbol}")
            for i in range(HistoricalDataService.RETRIES):
                try:
                    print(f"DEBUG: YFinance Fetch Attempt {i+1} for {symbol}")
                    df = HistoricalDataService.fetch_yfinance(symbol, timeframe, lookback_months)
                    HistoricalDataService.save_cache(symbol, timeframe, df)
                    return df, {"status": "SUCCESS", "data_source": "YFINANCE", "candle_count": len(df)}
                except Exception as e:
                    errors[f"yfinance_attempt_{i+1}"] = str(e)
                    time.sleep(HistoricalDataService.BACKOFF * (i + 1))

        # 4. Critical Failure
        final_error = {
            "status": "DATA_FETCH_FAILED",
            "symbol": symbol,
            "errors": errors,
            "action_required": [
                "Ensure MT5 Terminal is logged in",
                "Check symbol exists in Market Watch",
                "Verify internet connection for YFinance fallback"
            ]
        }
        print(f"CRITICAL: Historical data fetching failed for {symbol}: {errors}")
        raise RuntimeError(final_error)

    @staticmethod
    def data_health(symbol):
        """Returns health status for a symbol across sources."""
        health = {
            "symbol": symbol,
            "mt5": MT5Connector.check_connection(),
            "cache": HistoricalDataService.load_cache(symbol, "D1") is not None
        }
        try:
            HistoricalDataService.fetch_yfinance(symbol, "D1", 1)
            health["yfinance"] = "OK"
        except Exception as e:
            health["yfinance"] = str(e)
        return health
