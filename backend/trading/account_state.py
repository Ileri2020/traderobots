import MetaTrader5 as mt5
from backend.trading.user_mt5_manager import UserMT5Manager # Import as absolute if possible or relative
# Adjust import based on python path. Since this is in backend/trading, and UserMT5Manager in same dir:
# But we might need full path if Django runs from root.
# Let's use relative import or full package path.
try:
    from trading.user_mt5_manager import UserMT5Manager
except ImportError:
    from .user_mt5_manager import UserMT5Manager

def get_live_account_state(account):
    mt5m = UserMT5Manager(account.user.id, account)
    mt5m.connect()

    info = mt5.account_info()
    if info is None:
        mt5m.shutdown()
        raise Exception("Unable to fetch account info")

    data = {
        "balance": info.balance,
        "equity": info.equity,
        "margin": info.margin,
        "free_margin": info.margin_free,
        "profit": info.profit,
        "currency": info.currency,
    }

    mt5m.shutdown()
    return data
