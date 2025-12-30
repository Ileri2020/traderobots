import pandas as pd
import numpy as np

class IndicatorEngine:
    @staticmethod
    def calculate_sma(data, period=14):
        return data['close'].rolling(window=period).mean()

    @staticmethod
    def calculate_ema(data, period=14):
        return data['close'].ewm(span=period, adjust=False).mean()

    @staticmethod
    def calculate_rsi(data, period=14):
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def calculate_macd(data, fast=12, slow=26, signal=9):
        exp1 = data['close'].ewm(span=fast, adjust=False).mean()
        exp2 = data['close'].ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        return macd, signal_line

    @staticmethod
    def calculate_bollinger_bands(data, period=20, std=2):
        sma = data['close'].rolling(window=period).mean()
        std_dev = data['close'].rolling(window=period).std()
        upper = sma + (std_dev * std)
        lower = sma - (std_dev * std)
        return upper, sma, lower

    @staticmethod
    def calculate_atr(data, period=14):
        high_low = data['high'] - data['low']
        high_close = np.abs(data['high'] - data['close'].shift())
        low_close = np.abs(data['low'] - data['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        return true_range.rolling(window=period).mean()

    @staticmethod
    def calculate_stochastic(data, k_period=14, d_period=3):
        low_min = data['low'].rolling(window=k_period).min()
        high_max = data['high'].rolling(window=k_period).max()
        k = 100 * (data['close'] - low_min) / (high_max - low_min)
        d = k.rolling(window=d_period).mean()
        return k, d

    @staticmethod
    def calculate_adx(data, period=14):
        # simplified ADX
        plus_dm = data['high'].diff()
        minus_dm = data['low'].diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        minus_dm = np.abs(minus_dm)
        
        atr = IndicatorEngine.calculate_atr(data, period)
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        return adx, plus_di, minus_di
