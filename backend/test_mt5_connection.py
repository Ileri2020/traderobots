"""
MT5 Connection Test Script (Verbose)
-----------------------------------
What this tests:
1. MT5 terminal initialization (IPC)
2. Account authorization
3. Account info retrieval
4. Symbol availability
5. Historical data fetch (EURUSD H1)

Requirements:
- MetaTrader 5 terminal INSTALLED and RUNNING on this machine
- Python package: MetaTrader5
"""

import MetaTrader5 as mt5
import sys
import platform
from datetime import datetime
import time
import psutil
import os
from dotenv import load_dotenv

load_dotenv()

arch = platform.architecture()[0]
print(f"Python architecture: {arch}")

# ========= MT5 CREDENTIALS (for testing only) =========
MT5_PATH = os.getenv("MT5_PATH", r"C:\Program Files\XM Global MT5\terminal64.exe")
login = 100690024
password = "R9JzFCyBFD@QZPT"
server = "XMGlobal-MT5 5"
TIMEOUT = 60000  # 30 seconds
SYMBOL = "EURUSD"



# server = "MetaQuotes-Demo"
# login = 5043053597
# password = "VvE!Av5w"

# =====================================================

def fail(msg):
    print(f"\n❌ FAIL: {msg}")
    print("Last MT5 error:", mt5.last_error())
    mt5.shutdown()
    sys.exit(1)

def ok(msg):
    print(f"✅ {msg}")

def is_mt5_running():
    """Check if MetaTrader 5 terminal process exists."""
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and "terminal64.exe" in proc.info['name']:
            return True
    return False

def main():
    mt5.shutdown()
    time.sleep(2)  # small wait after shutdown
    print("\n===== MT5 CONNECTION TEST START =====")
    print(f"Time: {datetime.now()}\n")

    # Step 0: Check if MT5 is already running
    running = is_mt5_running()
    print(f"→ MT5 already running? {'Yes' if running else 'No'}")

    if running:
        print("→ Attempting to connect to running MT5 instance...")
    else:
        print("→ MT5 not running, will launch via Python initialize()")

    # Clean start
    mt5.shutdown()
    time.sleep(2)  # small wait after shutdown

    # 1️⃣ Initialize MT5
    print(f"→ Initializing MT5 terminal from: {MT5_PATH}")
    initialized = mt5.initialize(path=MT5_PATH)
    # initialized = mt5.initialize(
    #     path=MT5_PATH,
    #     login=MT5_LOGIN,
    #     password=MT5_PASSWORD,
    #     server=MT5_SERVER,
    #     timeout=TIMEOUT,
    #     portable=False  
    # )

    mt5.login(login, password, server)

    if not initialized:
        code, msg = mt5.last_error()
        fail(f"Initialization failed ({code}): {msg}")

    ok("MT5 initialized successfully")

    # 2️⃣ Check account authorization
    print("→ Retrieving account info...")
    account = mt5.account_info()
    if account is None:
        fail("MT5 initialized but account authorization FAILED")

    ok(f"Authorized account: {account.login}")
    print(f"   Balance: {account.balance}")
    print(f"   Equity:  {account.equity}")
    print(f"   Server:  {account.server}")

    # 3️⃣ Symbol check
    print(f"\n→ Selecting symbol: {SYMBOL}")
    if not mt5.symbol_select(SYMBOL, True):
        code, msg = mt5.last_error()
        fail(f"Symbol {SYMBOL} not available in Market Watch ({code}: {msg})")

    ok(f"Symbol {SYMBOL} selected")

    # 4️⃣ Historical data fetch
    print(f"→ Fetching historical candles ({SYMBOL}, H1, 500 bars)...")
    rates = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_H1, 0, 500)

    if rates is None:
        code, msg = mt5.last_error()
        fail(f"Historical data fetch returned None ({code}: {msg})")
    elif len(rates) == 0:
        fail("Historical data fetch returned 0 bars")

    ok(f"Fetched {len(rates)} candles")

    first = rates[0]
    last = rates[-1]
    print(f"   From: {datetime.fromtimestamp(first['time'])}")
    print(f"   To:   {datetime.fromtimestamp(last['time'])}")

    # 5️⃣ Final verdict
    print("\n🎉 MT5 CONNECTION TEST PASSED")
    print("✔ Terminal reachable")
    print("✔ Account authorized")
    print("✔ IPC healthy")
    print("✔ Market data accessible")

    mt5.shutdown()
    print("===== TEST COMPLETE =====\n")

if __name__ == "__main__":
    
    main()
