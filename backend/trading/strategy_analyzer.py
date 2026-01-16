import pandas as pd
import numpy as np
import math
from datetime import datetime, timedelta
from .data_service import HistoricalDataService

class StrategyAnalyzer:
    """
    Core engine for Historical-Data-Driven Conditional Execution.
    """
    
    def __init__(self, robot):
        self.robot = robot
        self.lookback = robot.historical_lookback
        self.recency_bias = robot.recency_bias
        self.session_pref = robot.session_preference
        self.symbol = robot.symbol
        self.indicators = robot.indicators # List from JSON

    def analyze(self):
        """
        Execution flow:
        1. Fetch Data
        2. Calculate Weights
        3. Indicator Analysis -> Probability
        4. Determine Entry Zone
        """
        # 1. Fetch & Normalize
        # Use allow_fallback based on robot preference or system default (True for now)
        try:
            df, report = HistoricalDataService.fetch_data(self.symbol, "H1", self.lookback)
        except Exception as e:
            return {
                "status": "FAILED",
                "reason": str(e)
            }
            
        if df.empty:
            return {
                "status": "FAILED",
                "reason": "No historical data available"
            }
        
        # Normalize Data (ensure session column exists)
        df = self.normalize_data(df)
        
        # 2. Add technical indicators (using pandas_ta if available or custom)
        # ... rest of analysis logic ...
    
    def normalize_data(self, df):
        """Add session and time features"""
        if df.empty: return df
        df['hour'] = df['time'].dt.hour
        df['day_of_week'] = df['time'].dt.dayofweek
        
        # Simple session marking (UTC assumed for simplicity)
        # Asia: 0-8, London: 8-16, NY: 13-21
        conditions = [
            (df['hour'] >= 0) & (df['hour'] < 8),
            (df['hour'] >= 8) & (df['hour'] < 16),
            (df['hour'] >= 13) & (df['hour'] < 21)
        ]
        choices = ['ASIA', 'LONDON', 'NY']
        df['session'] = np.select(conditions, choices, default='OTHER')
        return df
        
        # 2. Add technical indicators (using pandas_ta if available or custom)
        # This part assumes we have a way to calculate them. 
        # For this prototype, we'll simulate indicator signals.
        
        # 3. Calculate Weights
        now = datetime.now()
        df['time_diff_hours'] = (now - df['time']).dt.total_seconds() / 3600
        # w_i = exp(-λ * Δt)
        # We assume Δt is normalized or scaled appropriately. 
        # Let's normalize time diff to [0, 1] for the period or just use hours?
        # Using raw hours might make weights tiny if lambda is 0.1.
        # Lambda default 0.1 -> exp(-0.1 * 10) = 0.36. exp(-0.1 * 100) = 0.000045.
        # This seems aggressive for hours. Scaling lambda? Or assuming Δt is 'days'?
        # Let's treat Δt as 'days'.
        df['time_diff_days'] = df['time_diff_hours'] / 24.0
        df['recency_weight'] = np.exp(-self.recency_bias * df['time_diff_days'])
        
        # Session match
        if self.session_pref != 'ANY':
            df['session_weight'] = np.where(df['session'] == self.session_pref, 1.5, 0.5)
        else:
            df['session_weight'] = 1.0
            
        df['total_weight'] = df['recency_weight'] * df['session_weight']
        
        # 4. Simulate finding "Trade-worthy moments"
        # In a real engine, we'd check strict indicator rules here.
        # Prototype: Find where Close < SMA (Buy Dip) or Close > SMA (Sell Top)
        # Using a simplistic 'signal' logic for demonstration.
        
        # Let's calculate a simple SMA
        df['SMA'] = df['close'].rolling(window=50).mean()
        
        # Identify "Bullish Context" rows (e.g., Price > SMA)
        bullish_rows = df[df['close'] > df['SMA']]
        bearish_rows = df[df['close'] < df['SMA']]
        
        current_price = df['close'].iloc[-1]
        
        # Determine likely direction based on weighted recency of trends
        # Sum weights of bullish vs bearish recent candles?
        bullish_score = bullish_rows['total_weight'].sum()
        bearish_score = bearish_rows['total_weight'].sum()
        
        direction = "BUY" if bullish_score > bearish_score else "SELL"
        confidence = max(bullish_score, bearish_score) / (bullish_score + bearish_score + 0.0001)
        
        # 5. Determine Entry Zone (Conditional)
        # If BUY -> Look for recent pullbacks (e.g., lower quartiles of recent candles)
        # If SELL -> Look for recent spikes
        
        # Let's look at last 100 candles weighted
        recent = df.tail(100)
        
        volatility = recent['high'].max() - recent['low'].min()
        
        if direction == "BUY":
            # Buy Limit: Target a lower price than current
            # e.g., current - 0.2 * volatility
            entry_target = current_price - (0.1 * volatility)
            entry_type = "BUY_LIMIT"
            sl = entry_target - (0.5 * volatility)
            tp = entry_target + (volatility)
        else:
            # Sell Limit
            entry_target = current_price + (0.1 * volatility)
            entry_type = "SELL_LIMIT"
            sl = entry_target + (0.5 * volatility)
            tp = entry_target - (volatility)
            
        if confidence < self.robot.confidence_threshold:
            return {
                "status": "IDLE", 
                "reason": f"Confidence {confidence:.2f} below threshold {self.robot.confidence_threshold}",
                "confidence": confidence
            }
            
        return {
            "status": "ORDER_PLACED",
            "entry_type": entry_type,
            "direction": direction,
            "target_entry": round(entry_target, 5),
            "sl": round(sl, 5),
            "tp": round(tp, 5),
            "confidence": round(confidence, 2),
            "expiry": (datetime.now() + timedelta(minutes=self.robot.max_entry_wait_minutes)).isoformat()
        }
