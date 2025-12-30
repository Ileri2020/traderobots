import json

class RobotGenerator:
    @staticmethod
    def generate_mql5(robot_name, symbol, timeframe, rules, risk):
        """
        Generates MQL5 code for a given strategy.
        rules: dict of signals, e.g. {'rsi': {'buy': 30, 'sell': 70}, 'ma': {'period': 50, 'type': 'SMA'}}
        risk: dict with lot, sl, tp
        """
        
        # Initialize handles and variables
        init_code = ""
        deinit_code = ""
        
        # Logic for boolean checks
        buy_conditions = []
        sell_conditions = []
        
        global_vars = ""
        
        signal_logic = ""

        # Helper to add indicator logic
        def add_indicator(name, globals_str, init_str, deinit_str, logic_str, buy_cond, sell_cond):
            nonlocal global_vars, init_code, deinit_code, signal_logic
            global_vars += globals_str
            init_code += init_str
            deinit_code += deinit_str
            signal_logic += logic_str
            buy_conditions.append(buy_cond)
            sell_conditions.append(sell_cond)

        # RSI Implementation
        if 'rsi' in rules:
            add_indicator(
                "RSI",
                "int handle_rsi;\n",
                f"   handle_rsi = iRSI(_Symbol, _Period, {rules['rsi'].get('period', 14)}, PRICE_CLOSE);\n"
                "   if(handle_rsi == INVALID_HANDLE) return(INIT_FAILED);\n",
                "   IndicatorRelease(handle_rsi);\n",
                f"""
bool CheckRSI(bool is_buy)
{{
   double rsi[];
   CopyBuffer(handle_rsi, 0, 0, 2, rsi);
   ArraySetAsSeries(rsi, true);
   if(is_buy) return rsi[0] < {rules['rsi'].get('buy', 30)};
   else return rsi[0] > {rules['rsi'].get('sell', 70)};
}}
""",
                "CheckRSI(true)",
                "CheckRSI(false)"
            )

        # Moving Average Implementation
        if 'ma' in rules:
            ma_method = rules['ma'].get('type', 'MODE_SMA')
            add_indicator(
                "MA",
                "int handle_ma;\n",
                f"   handle_ma = iMA(_Symbol, _Period, {rules['ma'].get('period', 50)}, 0, {ma_method}, PRICE_CLOSE);\n"
                "   if(handle_ma == INVALID_HANDLE) return(INIT_FAILED);\n",
                "   IndicatorRelease(handle_ma);\n",
                """
bool CheckMA(bool is_buy)
{{
   double ma[];
   CopyBuffer(handle_ma, 0, 0, 2, ma);
   ArraySetAsSeries(ma, true);
   double price = is_buy ? SymbolInfoDouble(_Symbol, SYMBOL_ASK) : SymbolInfoDouble(_Symbol, SYMBOL_BID);
   if(is_buy) return price > ma[0];
   else return price < ma[0];
}}
""",
                "CheckMA(true)",
                "CheckMA(false)"
            )

        # MACD Implementation
        if 'macd' in rules:
            add_indicator(
                "MACD",
                "int handle_macd;\n",
                f"   handle_macd = iMACD(_Symbol, _Period, 12, 26, 9, PRICE_CLOSE);\n"
                "   if(handle_macd == INVALID_HANDLE) return(INIT_FAILED);\n",
                "   IndicatorRelease(handle_macd);\n",
                """
bool CheckMACD(bool is_buy)
{{
   double macd_main[], macd_signal[];
   CopyBuffer(handle_macd, 0, 0, 2, macd_main);
   CopyBuffer(handle_macd, 1, 0, 2, macd_signal);
   ArraySetAsSeries(macd_main, true);
   ArraySetAsSeries(macd_signal, true);
   if(is_buy) return macd_main[0] > macd_signal[0] && macd_main[1] <= macd_signal[1];
   else return macd_main[0] < macd_signal[0] && macd_main[1] >= macd_signal[1];
}}
""",
                "CheckMACD(true)",
                "CheckMACD(false)"
            )
            
        # Bollinger Bands Implementation
        if 'bands' in rules:
             add_indicator(
                "Bands",
                "int handle_bands;\n",
                f"   handle_bands = iBands(_Symbol, _Period, {rules['bands'].get('period', 20)}, 0, {rules['bands'].get('dev', 2.0)}, PRICE_CLOSE);\n"
                "   if(handle_bands == INVALID_HANDLE) return(INIT_FAILED);\n",
                "   IndicatorRelease(handle_bands);\n",
                """
bool CheckBands(bool is_buy)
{{
   double upper[], lower[];
   if(is_buy) {
        CopyBuffer(handle_bands, 2, 0, 2, lower);
        ArraySetAsSeries(lower, true);
        return SymbolInfoDouble(_Symbol, SYMBOL_ASK) < lower[0];
   } else {
        CopyBuffer(handle_bands, 1, 0, 2, upper);
        ArraySetAsSeries(upper, true);
        return SymbolInfoDouble(_Symbol, SYMBOL_BID) > upper[0];
   }
}}
""",
                "CheckBands(true)",
                "CheckBands(false)"
            )

        # Stochastic Implementation
        if 'stoch' in rules:
            add_indicator(
                "Stoch",
                "int handle_stoch;\n",
                f"   handle_stoch = iStochastic(_Symbol, _Period, 5, 3, 3, MODE_SMA, STO_LOWHIGH);\n"
                "   if(handle_stoch == INVALID_HANDLE) return(INIT_FAILED);\n",
                "   IndicatorRelease(handle_stoch);\n",
                """
bool CheckStoch(bool is_buy)
{{
   double main_stoch[], signal_stoch[];
   CopyBuffer(handle_stoch, 0, 0, 2, main_stoch);
   CopyBuffer(handle_stoch, 1, 0, 2, signal_stoch);
   ArraySetAsSeries(main_stoch, true); ArraySetAsSeries(signal_stoch, true);
   if(is_buy) return main_stoch[0] < 20 && main_stoch[0] > signal_stoch[0];
   else return main_stoch[0] > 80 && main_stoch[0] < signal_stoch[0];
}}
""",
                "CheckStoch(true)",
                "CheckStoch(false)"
            )
            
        buy_cond_str = " && ".join(buy_conditions) if buy_conditions else "false"
        sell_cond_str = " && ".join(sell_conditions) if sell_conditions else "false"

        code = f"""//+------------------------------------------------------------------+
//|                                              {robot_name}.mq5 |
//|                                  Generated by Traderobots AI |
//|                                             https://traderobots.ai |
//+------------------------------------------------------------------+
#property copyright "Traderobots AI"
#property link      "https://traderobots.ai"
#property version   "1.00"
#property strict

//--- Input parameters
input double   InpLots      = {risk.get('lot', 0.01)};    // Lot size
input int      InpStopLoss  = {risk.get('sl', 30)};      // Stop Loss in points
input int      InpTakeProfit= {risk.get('tp', 60)};      // Take Profit in points

//--- Global variables
{global_vars}

//--- Signal Logic Functions
{signal_logic}

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{{
{init_code}
   return(INIT_SUCCEEDED);
}}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{{
{deinit_code}
}}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{{
   if(!TerminalInfoInteger(TERMINAL_CONNECTED)) return;
   
   // Check for open positions
   if(PositionsTotal() == 0)
   {{
      // Buy Signal
      if({buy_cond_str})
      {{
         TradeBuy();
      }}
      // Sell Signal
      else if({sell_cond_str})
      {{
         TradeSell();
      }}
   }}
}}

void TradeBuy()
{{
   MqlTradeRequest request={{0}};
   MqlTradeResult  result={{0}};
   
   request.action   = TRADE_ACTION_DEAL;
   request.symbol   = _Symbol;
   request.volume   = InpLots;
   request.type     = ORDER_TYPE_BUY;
   request.price    = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   request.sl       = request.price - InpStopLoss * _Point;
   request.tp       = request.price + InpTakeProfit * _Point;
   request.deviation= 10;
   request.magic    = 123456;
   
   OrderSend(request, result);
}}

void TradeSell()
{{
   MqlTradeRequest request={{0}};
   MqlTradeResult  result={{0}};
   
   request.action   = TRADE_ACTION_DEAL;
   request.symbol   = _Symbol;
   request.volume   = InpLots;
   request.type     = ORDER_TYPE_SELL;
   request.price    = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   request.sl       = request.price + InpStopLoss * _Point;
   request.tp       = request.price - InpTakeProfit * _Point;
   request.deviation= 10;
   request.magic    = 123456;
   
   OrderSend(request, result);
}}
"""
        return code

    @staticmethod
    def generate_python(robot_name, symbol, timeframe, rules, risk, account_id, password, server):
        """
        Generates Python code using MetaTrader5 library for the strategy.
        Now includes logic for RSI, MA, MACD, Bollinger Bands, and Stochastic using pandas_ta.
        """
        
        # 1. Build Indicator Calculations and Logic
        calc_lines = []
        buy_conds = []
        sell_conds = []

        # RSI
        if 'rsi' in rules:
            p = rules['rsi'].get('period', 14)
            buy_val = rules['rsi'].get('buy', 30)
            sell_val = rules['rsi'].get('sell', 70)
            calc_lines.append(f"    # RSI\n    df['rsi'] = df.ta.rsi(length={p})")
            buy_conds.append(f"(df['rsi'].iloc[-1] < {buy_val})")
            sell_conds.append(f"(df['rsi'].iloc[-1] > {sell_val})")

        # MA
        if 'ma' in rules:
            p = rules['ma'].get('period', 50)
            # Default to SMA for simplicity in python script, could check 'type' maps to sma/ema
            calc_lines.append(f"    # MA\n    df['ma'] = df.ta.sma(length={p})")
            buy_conds.append("(df['close'].iloc[-1] > df['ma'].iloc[-1])")
            sell_conds.append("(df['close'].iloc[-1] < df['ma'].iloc[-1])")

        # MACD
        if 'macd' in rules:
            # macd(fast=12, slow=26, signal=9) returns columns: MACD_12_26_9, MACDh_12_26_9, MACDs_12_26_9
            calc_lines.append("    # MACD\n    macd = df.ta.macd(fast=12, slow=26, signal=9)")
            calc_lines.append("    df = pd.concat([df, macd], axis=1)")
            # MQL5: buy if main > signal (crossover?) or main > signal 
            # Simplified Logic: Buy if MACD line > Signal line
            # Column names from pandas_ta usually: MACD_12_26_9 (Main), MACDs_12_26_9 (Signal)
            buy_conds.append("(df.iloc[-1]['MACD_12_26_9'] > df.iloc[-1]['MACDs_12_26_9'])")
            sell_conds.append("(df.iloc[-1]['MACD_12_26_9'] < df.iloc[-1]['MACDs_12_26_9'])")

        # Bollinger Bands
        if 'bands' in rules:
            p = rules['bands'].get('period', 20)
            d = rules['bands'].get('dev', 2.0)
            # bbands returns BBL, BBM, BBU
            calc_lines.append(f"    # Bands\n    bands = df.ta.bbands(length={p}, std={d})")
            calc_lines.append("    df = pd.concat([df, bands], axis=1)")
            # Columns: BBL_{p}_{d}, BBU_{p}_{d}
            # Buy if price < Lower, Sell if price > Upper
            low_col = f"BBL_{p}_{d}"
            up_col = f"BBU_{p}_{d}"
            buy_conds.append(f"(df['close'].iloc[-1] < df.iloc[-1]['{low_col}'])")
            sell_conds.append(f"(df['close'].iloc[-1] > df.iloc[-1]['{up_col}'])")

        # Stochastic
        if 'stoch' in rules:
            # stoch(k=5, d=3, smooth_k=3) returns STOCHk, STOCHd
            calc_lines.append("    # Stoch\n    stoch = df.ta.stoch(k=5, d=3, smooth_k=3)")
            calc_lines.append("    df = pd.concat([df, stoch], axis=1)")
            # Columns: STOCHk_5_3_3, STOCHd_5_3_3
            buy_conds.append("(df.iloc[-1]['STOCHk_5_3_3'] < 20 and df.iloc[-1]['STOCHk_5_3_3'] > df.iloc[-1]['STOCHd_5_3_3'])")
            sell_conds.append("(df.iloc[-1]['STOCHk_5_3_3'] > 80 and df.iloc[-1]['STOCHk_5_3_3'] < df.iloc[-1]['STOCHd_5_3_3'])")

        # Combine
        calc_code = "\n".join(calc_lines) if calc_lines else "    pass"
        buy_expr = " and ".join(buy_conds) if buy_conds else "False"
        sell_expr = " and ".join(sell_conds) if sell_conds else "False"

        # Python script structure
        python_script = f"""
import MetaTrader5 as mt5
import time
import pandas as pd
import pandas_ta as ta
from datetime import datetime

# Creds & Settings
LOGIN = {account_id}
PASSWORD = "{password}"
SERVER = "{server}"
SYMBOL = "{symbol}"
TIMEFRAME = mt5.TIMEFRAME_{timeframe}
LOT_SIZE = {risk.get('lot', 0.01)}
SL_POINTS = {risk.get('sl', 30)}
TP_POINTS = {risk.get('tp', 60)}

def connect():
    if not mt5.initialize(login=LOGIN, server=SERVER, password=PASSWORD):
        print("initialize() failed, error code =", mt5.last_error())
        return False
    return True

def get_data():
    rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, 100)
    if rates is None:
        return None
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df

def signal_check(df):
    if len(df) < 50: return None
    
{calc_code}
    
    # Logic Checks
    if {buy_expr}:
        return 'buy'
    elif {sell_expr}:
        return 'sell'
        
    return None

def execute_trade(signal):
    point = mt5.symbol_info(SYMBOL).point
    price = mt5.symbol_info_tick(SYMBOL).ask if signal == 'buy' else mt5.symbol_info_tick(SYMBOL).bid
    
    request = {{
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": LOT_SIZE,
        "type": mt5.ORDER_TYPE_BUY if signal == 'buy' else mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": price - SL_POINTS * point if signal == 'buy' else price + SL_POINTS * point,
        "tp": price + TP_POINTS * point if signal == 'buy' else price - TP_POINTS * point,
        "deviation": 10,
        "magic": 234000,
        "comment": "python ai bot",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }}
    
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("order_send failed, retcode={{}}".format(result.retcode))
    else:
        print(f"Trade executed: {{signal}}")

def main():
    if not connect():
        print("Failed to connect to MT5")
        return
        
    print(f"Bot {robot_name} started on {{SYMBOL}}. Waiting for signals...")
    
    while True:
        try:
            df = get_data()
            if df is not None:
                sig = signal_check(df)
                if sig:
                    # Check positions
                    positions = mt5.positions_get(symbol=SYMBOL)
                    if positions is None or len(positions) == 0:
                        print(f"Signal {{sig}} detected! Executing...")
                        execute_trade(sig)
                    else:
                        print(f"Signal {{sig}} detected but position exists.")
            
            time.sleep(60) # check every minute
        except Exception as e:
            print(f"Error in main loop: {{e}}")
            time.sleep(10)

if __name__ == "__main__":
    main()
"""
        return python_script
