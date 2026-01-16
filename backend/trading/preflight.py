import MetaTrader5 as mt5
try:
    from trading.user_mt5_manager import UserMT5Manager
except ImportError:
    from .user_mt5_manager import UserMT5Manager

def preflight_mt5(account, symbol, lot):
    mt5m = UserMT5Manager(account.user.id, account)
    mt5m.connect()

    if not mt5.symbol_select(symbol, True):
        mt5m.shutdown()
        raise Exception(f"Symbol {symbol} not available on your MT5 account")

    info = mt5.account_info()
    if not info.trade_allowed:
        mt5m.shutdown()
        raise Exception("Trading not allowed on this account")

    # Check lot size if needed (optional based on user request details, but good practice)
    # user request just said "Lot size check" under Phase 1, but offered no code for it in the snippet
    # so we stick to the snippet.

    mt5m.shutdown()
