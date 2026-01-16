import yfinance as yf
import requests
import pandas as pd

def test_yfinance_raw(symbol):
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    })
    
    print(f"Testing {symbol} with yfinance...")
    try:
        # Try history first
        ticker = yf.Ticker(symbol, session=session)
        df = ticker.history(period="1mo", interval="1h")
        if not df.empty:
            print(f"SUCCESS (history): {len(df)} rows")
            return True
    except Exception as e:
        print(f"History failed: {e}")
        
    try:
        # Try download
        df = yf.download(symbol, period="1mo", interval="1h", session=session, progress=False)
        if not df.empty:
            print(f"SUCCESS (download): {len(df)} rows")
            return True
    except Exception as e:
        print(f"Download failed: {e}")
        
    return False

def test_yfinance_manual(symbol):
    from curl_cffi import requests as crequests
    import time
    
    end = int(time.time())
    start = end - (30 * 24 * 3600)
    url = f"https://query1.finance.yahoo.com/v7/finance/download/{symbol}?period1={start}&period2={end}&interval=1d&events=history"
    
    print(f"Testing manual fetch for {symbol}...")
    try:
        r = crequests.get(url, impersonate="chrome110")
        if r.status_code == 200:
            print(f"SUCCESS (manual): {len(r.text)} bytes")
            # print(r.text[:200])
            return True
        else:
            print(f"FAILED (manual): Status {r.status_code}")
            return False
    except Exception as e:
        print(f"Manual fetch failed: {e}")
        return False

if __name__ == "__main__":
    test_yfinance_raw("EURUSD=X")
    test_yfinance_manual("EURUSD=X")
    test_yfinance_manual("JPY=X")
