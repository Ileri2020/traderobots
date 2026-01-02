try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None

import os
import numpy as np
from dotenv import load_dotenv

load_dotenv()

class MT5Connector:
    @staticmethod
    def initialize():
        if mt5 is None:
            print("unable to load mt5")
            return False
            
        try:
            if not mt5.initialize():
                return False
            
            login_str = os.getenv("MT5_LOGIN", "0")
            login = int(login_str) if login_str.isdigit() else 0
            password = os.getenv("MT5_PASSWORD", "")
            server = os.getenv("MT5_SERVER", "")
            
            if login == 0: return False

            if not mt5.login(login, password=password, server=server):
                return False
                
            return True
        except Exception:
            return False

    @staticmethod
    def get_account_info():
        if not MT5Connector.initialize():
            return None
        
        account_info = mt5.account_info()
        if account_info is None:
            return None
            
        return account_info._asdict()

    @staticmethod
    def get_market_data(symbol, timeframe, n_bars=1000):
        if not MT5Connector.initialize():
            return None
            
        tf_map = {
            'M1': mt5.TIMEFRAME_M1,
            'M5': mt5.TIMEFRAME_M5,
            'M15': mt5.TIMEFRAME_M15,
            'H1': mt5.TIMEFRAME_H1,
            'H4': mt5.TIMEFRAME_H4,
            'D1': mt5.TIMEFRAME_D1,
        }
        
        mt5_tf = tf_map.get(timeframe, mt5.TIMEFRAME_H1)
        rates = mt5.copy_rates_from_pos(symbol, mt5_tf, 0, n_bars)
        
        if rates is None:
            return None
            
        return rates

    @staticmethod
    def place_order(symbol, lot, order_type, price=None, sl=0, tp=0):
        if not MT5Connector.initialize():
            return None
            
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": order_type,
            "price": price if price else mt5.symbol_info_tick(symbol).ask if order_type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).bid,
            "sl": sl,
            "tp": tp,
            "magic": 123456,
            "comment": "Traderobots AI Order",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        return result

    @staticmethod
    def shutdown():
        if mt5:
            mt5.shutdown()
