import pandas as pd
from .indicator_engine import IndicatorEngine

class Backtester:
    def __init__(self, data, strategy_rules):
        """
        data: pd.DataFrame with OHLC
        strategy_rules: dict defining signals (e.g. {"rsi": {"buy": 30, "sell": 70}, "ma": {"period": 50}})
        """
        self.data = data
        self.rules = strategy_rules

    def run(self):
        # Calculate indicators as needed
        if 'rsi' in self.rules:
            self.data['rsi'] = IndicatorEngine.calculate_rsi(self.data, period=self.rules['rsi'].get('period', 14))
        
        if 'ma' in self.rules:
            self.data['ma'] = IndicatorEngine.calculate_sma(self.data, period=self.rules['ma'].get('period', 50))
            
        if 'macd' in self.rules:
            macd, signal = IndicatorEngine.calculate_macd(self.data)
            self.data['macd'] = macd
            self.data['macd_signal'] = signal

        trades = []
        position = None # None, 'long', 'short'
        
        for i in range(1, len(self.data)):
            row = self.data.iloc[i]
            prev_row = self.data.iloc[i-1]
            
            # Combine Signals
            buy_conditions = []
            sell_conditions = []
            
            if 'rsi' in self.rules:
                buy_conditions.append(row['rsi'] < self.rules['rsi'].get('buy', 30))
                sell_conditions.append(row['rsi'] > self.rules['rsi'].get('sell', 70))
                
            if 'ma' in self.rules:
                buy_conditions.append(row['close'] > row['ma'])
                sell_conditions.append(row['close'] < row['ma'])
                
            if 'macd' in self.rules and 'macd' in row and 'macd_signal' in row:
                buy_conditions.append(row['macd'] > row['macd_signal'] and prev_row['macd'] <= prev_row['macd_signal'])
                sell_conditions.append(row['macd'] < row['macd_signal'] and prev_row['macd'] >= prev_row['macd_signal'])

            buy_signal = all(buy_conditions) if buy_conditions else False
            sell_signal = all(sell_conditions) if sell_conditions else False
            
            # Entry / Exit
            if position is None:
                if buy_signal:
                    position = 'long'
                    trades.append({'entry_time': row.name, 'entry_price': row['close'], 'type': 'buy'})
                elif sell_signal:
                    position = 'short'
                    trades.append({'entry_time': row.name, 'entry_price': row['close'], 'type': 'sell'})
            
            elif position == 'long':
                # Exit if sell signal OR if stop loss/take profit hit (simplified here)
                if sell_signal: 
                    self._close_trade(trades, row, 'long')
                    position = None
            
            elif position == 'short':
                if buy_signal: 
                    self._close_trade(trades, row, 'short')
                    position = None

        return trades

    def _close_trade(self, trades, row, type):
        if not trades: return
        trades[-1]['exit_time'] = row.name
        trades[-1]['exit_price'] = row['close']
        if type == 'long':
            trades[-1]['profit'] = trades[-1]['exit_price'] - trades[-1]['entry_price']
        else:
            trades[-1]['profit'] = trades[-1]['entry_price'] - trades[-1]['exit_price']

    def compute_metrics(self, trades):
        if not trades:
            return {"win_rate": 0, "total_profit": 0}
            
        closed_trades = [t for t in trades if 'profit' in t]
        if not closed_trades:
             return {"win_rate": 0, "total_profit": 0, "total_trades": len(trades)}

        wins = [t for t in closed_trades if t['profit'] > 0]
        win_rate = len(wins) / len(closed_trades)
        total_profit = sum([t['profit'] for t in closed_trades])
        
        return {
            "win_rate": round(win_rate * 100, 2),
            "total_profit": round(total_profit, 5),
            "total_trades": len(trades)
        }
