try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None

import os
import time
import subprocess
import psutil
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class MT5Connector:
    # Default terminal path - adjust based on your installation if not in .env
    DEFAULT_PATH = os.getenv("MT5_PATH", r"C:\Program Files\XM Global MT5\terminal64.exe")
    PROCESS_NAME = "terminal64.exe"

    @staticmethod
    def is_mt5_running():
        """Checks if the MT5 terminal process is active."""
        for proc in psutil.process_iter(attrs=["name"]):
            try:
                if proc.info["name"].lower() == MT5Connector.PROCESS_NAME.lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False

    @staticmethod
    def start_mt5_terminal(wait_timeout=20):
        """Launches the MT5 terminal if it's not already running."""
        if MT5Connector.is_mt5_running():
            print("DEBUG: MT5 Terminal already running.")
            return True

        if not os.path.exists(MT5Connector.DEFAULT_PATH):
            print(f"ERROR: MT5 executable not found at {MT5Connector.DEFAULT_PATH}")
            return False

        print(f"DEBUG: Starting MT5 Terminal from {MT5Connector.DEFAULT_PATH}...")
        try:
            # Start in same user context, detached
            subprocess.Popen(
                [MT5Connector.DEFAULT_PATH],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=False
            )
            
            # Wait for process to appear
            start_time = time.time()
            while time.time() - start_time < wait_timeout:
                if MT5Connector.is_mt5_running():
                    print("DEBUG: MT5 Terminal process detected.")
                    # Extra sleep for UI/Login to initialize
                    time.sleep(5)
                    return True
                time.sleep(1)
        except Exception as e:
            print(f"ERROR: Failed to launch MT5: {e}")
            return False
            
        return False

    @staticmethod
    def connect_mt5(account_number, password, server, max_attempts=3):
        """
        Bulletproof MT5 connection with auto-launch and exponential backoff.
        """
        if mt5 is None:
            raise RuntimeError("MetaTrader5 library not installed.")
            
        if account_number is None:
            raise ValueError("Account number cannot be None.")
            
        try:
            login = int(account_number)
        except ValueError:
            raise ValueError(f"Account number must be numeric, got: {account_number}")

        # 1. Ensure terminal is running
        if not MT5Connector.is_mt5_running():
            if not MT5Connector.start_mt5_terminal():
                raise RuntimeError("Failed to auto-start MT5 terminal. Please start it manually.")

        last_error = ""
        base_delay = 2
        
        for attempt in range(1, max_attempts + 1):
            try:
                print(f"DEBUG: MT5 Connection Attempt {attempt} for {login}...")
                
                # Shutdown existing IPC session to avoid 10005 timeout
                mt5.shutdown()
                time.sleep(1) # Breath
                
                # IPC Connection
                init_params = {
                    "login": login,
                    "password": password,
                    "server": server,
                    "timeout": 20000
                }
                
                if os.path.exists(MT5Connector.DEFAULT_PATH):
                    init_params["path"] = MT5Connector.DEFAULT_PATH

                success = mt5.initialize(**init_params)
                
                if not success:
                    err_code, err_desc = mt5.last_error()
                    raise RuntimeError(f"MT5 initialization failed: {err_code} - {err_desc}")
                
                # Verify Account Info (Authorization Check)
                info = mt5.account_info()
                if info is None:
                    # Maybe it's still connecting, wait a bit
                    print("DEBUG: Connected but no account info. Waiting for authorization...")
                    time.sleep(3)
                    info = mt5.account_info()
                    
                if info is None:
                    raise RuntimeError("MT5 connected but account not authorized (Check login/password)")
                
                print(f"DEBUG: MT5 Successfully Connected & Authorized: Account {info.login}")
                return True

            except Exception as e:
                last_error = str(e)
                if attempt == max_attempts:
                    break
                
                delay = base_delay * (2 ** (attempt - 1))
                print(f"DEBUG: Attempt {attempt} failed: {last_error}. Retrying in {delay}s...")
                time.sleep(delay)
        
        raise RuntimeError(f"MT5 Authentication Failed after {max_attempts} attempts: {last_error}")

    @staticmethod
    def check_connection():
        """Watchdog: Checks current MT5 connection status and health."""
        if mt5 is None: 
            return {"connected": False, "error": "Library not installed"}
        
        # Check if terminal session is alive
        info = mt5.account_info()
        terminal = mt5.terminal_info()
        
        if info is None:
            return {"connected": False, "error": "No account session active"}

        return {
            "connected": True,
            "login": info.login,
            "server": info.server,
            "equity": info.equity,
            "balance": info.balance,
            "margin_free": info.margin_free,
            "leverage": info.leverage,
            "algo_trading": info.algo_trading,
            "terminal_connected": terminal.connected if terminal else False,
            "can_trade": info.algo_trading and (terminal.connected if terminal else False)
        }

    @staticmethod
    def get_market_data_range(symbol, timeframe_str, date_from, date_to, credentials=None):
        """
        Hardened MT5 fetcher with symbol matching and local data persistence.
        """
        if mt5 is None:
            raise RuntimeError("MT5 library not found")

        try:
            if credentials:
                MT5Connector.connect_mt5(
                    credentials.get('login'), 
                    credentials.get('password'), 
                    credentials.get('server')
                )
            
            tf_map = {
                'M1': mt5.TIMEFRAME_M1, 'M5': mt5.TIMEFRAME_M5, 'M15': mt5.TIMEFRAME_M15,
                'H1': mt5.TIMEFRAME_H1, 'H4': mt5.TIMEFRAME_H4, 'D1': mt5.TIMEFRAME_D1,
            }
            mt5_tf = tf_map.get(timeframe_str, mt5.TIMEFRAME_H1)
            
            # Auto-Symbol Matching
            actual_symbol = symbol
            if not mt5.symbol_select(symbol, True):
                print(f"DEBUG: Symbol {symbol} not found directly. Searching matches...")
                res = mt5.symbols_get()
                if res:
                    all_symbols = [s.name for s in res]
                    matches = [s for s in all_symbols if symbol.upper() in s.upper()]
                    if matches:
                        actual_symbol = matches[0]
                        print(f"DEBUG: MT5 Symbol matched to: {actual_symbol}")
                        mt5.symbol_select(actual_symbol, True)
                    else:
                        raise RuntimeError(f"Symbol {symbol} not available in MT5 Market Watch.")
                else:
                    raise RuntimeError(f"Could not retrieve symbols from MT5. Ensure you are logged in.")

            rates = mt5.copy_rates_range(actual_symbol, mt5_tf, date_from, date_to)
            
            if rates is None or len(rates) == 0:
                # Nudge terminal cache
                mt5.copy_rates_from_pos(actual_symbol, mt5_tf, 0, 500)
                time.sleep(1)
                rates = mt5.copy_rates_range(actual_symbol, mt5_tf, date_from, date_to)

            if rates is None or len(rates) == 0:
                raise RuntimeError(f"MT5 returned no data for {actual_symbol}")

            df = pd.DataFrame(rates)
            df["time"] = pd.to_datetime(df["time"], unit="s")
            
            # --- PERSISTENCE: Save to Local Cache ---
            try:
                # Use absolute path to ensure folder existence
                history_dir = Path("backend/data/history")
                history_dir.mkdir(parents=True, exist_ok=True)
                
                cache_name = f"{actual_symbol}_{timeframe_str}.csv"
                df.to_csv(history_dir / cache_name, index=False)
                print(f"DEBUG: Historical data persisted to {history_dir / cache_name}")
            except Exception as pe:
                print(f"WARNING: Data persistence failed: {pe}")

            return df
        except Exception as e:
            print(f"ERROR: MT5 Fetch Failure: {str(e)}")
            raise e

    @staticmethod
    def deploy_ea(robot_id, symbol, timeframe_str):
        """
        Deployment Life-cycle: Open chart and signal EA activity.
        In production, this would manage .mq5 compilation and template application.
        """
        if mt5 is None: return False
        
        tf_map = {
            'M1': mt5.TIMEFRAME_M1, 'M5': mt5.TIMEFRAME_M5, 'M15': mt5.TIMEFRAME_M15,
            'H1': mt5.TIMEFRAME_H1, 'D1': mt5.TIMEFRAME_D1,
        }
        
        chart_id = mt5.chart_open(symbol, tf_map.get(timeframe_str, mt5.TIMEFRAME_H1))
        if chart_id:
            print(f"DEBUG: Opened chart {chart_id} for {symbol}. Applying EA Robot_{robot_id}...")
            # Note: chart_apply_template is the standard way to attach EAs via Python
            return True
        return False

    @staticmethod
    def check_heartbeat(robot_id, max_age_seconds=60):
        """
        Checks if the EA for a specific robot is alive by checking a heartbeat file 
        written by the MQL5 code in the common files folder.
        """
        try:
            from django.conf import settings
            # MT5 Common Files Path (Standard Windows Location)
            common_path = Path(os.path.expandvars(r"%APPDATA%\MetaQuotes\Terminal\Common\Files"))
            hb_file = common_path / f"robot_{robot_id}.hb"
            
            if not hb_file.exists():
                return False
                
            mtime = os.path.getmtime(hb_file)
            age = time.time() - mtime
            return age < max_age_seconds
        except:
            return False

    @staticmethod
    def place_order(symbol, lot, order_type, price=None, sl=0, tp=0, credentials=None):
        try:
            if credentials:
                MT5Connector.connect_mt5(
                    credentials.get('login'), 
                    credentials.get('password'), 
                    credentials.get('server')
                )
            
            # Health check before trade
            health = MT5Connector.check_connection()
            if not health['connected'] or not health['can_trade']:
                 return {"error": f"Trading disabled: MT5 status {health.get('error', 'Ready but Algotrading off')}"}

            # Symbol matching
            actual_symbol = symbol
            if not mt5.symbol_select(symbol, True):
                all_symbols = [s.name for s in mt5.symbols_get()]
                matches = [s for s in all_symbols if symbol.upper() in s.upper()]
                if matches:
                    actual_symbol = matches[0]
                    mt5.symbol_select(actual_symbol, True)
                else:
                    return {"error": f"Symbol {symbol} not found"}

            tick = mt5.symbol_info_tick(actual_symbol)
            if not tick:
                 return {"error": f"No tick price for {actual_symbol}"}
                 
            fill_price = price or (tick.ask if order_type == mt5.ORDER_TYPE_BUY else tick.bid)

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": actual_symbol,
                "volume": float(lot),
                "type": order_type,
                "price": fill_price,
                "sl": float(sl),
                "tp": float(tp),
                "magic": 234000,
                "comment": "Traderobots AI RealTrade",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(request)
            if result is None:
                return {"error": str(mt5.last_error())}
            return result._asdict()
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def shutdown():
        if mt5:
            mt5.shutdown()
