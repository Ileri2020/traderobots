import MetaTrader5 as mt5
import os
from dotenv import load_dotenv

load_dotenv()

# Use XM Global MT5 path
MT5_PATH = os.getenv("MT5_PATH", r"C:\Program Files\XM Global MT5\terminal64.exe")

print(f"Using MT5 path: {MT5_PATH}")
print("Initializing MT5...")

if not mt5.initialize(path=MT5_PATH):
    print("INIT FAILED:", mt5.last_error())
    quit()

info = mt5.account_info()
print("Account info:", info)

symbols = mt5.symbols_get()
print("Symbols loaded:", len(symbols) if symbols else 0)

mt5.shutdown()
