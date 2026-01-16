"""
Seed script to populate IndicatorTemplate database with common trading indicators
Run with: python manage.py shell < seed_indicators.py
Or: python seed_indicators.py (if Django setup is configured)
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'traderobots.settings')
django.setup()

from api.models import IndicatorTemplate

def seed_indicators():
    """Populate the database with indicator templates"""
    
    indicators = [
        {
            "name": "RSI",
            "category": "oscillator",
            "description": "Relative Strength Index - Measures momentum with overbought/oversold levels and divergence detection",
            "parameters": {
                "period": 14,
                "buy": 30,
                "sell": 70,
                "mode": "level",  # 'level' or 'divergence'
            },
            "mql5_snippet": """
int handle_rsi = iRSI(_Symbol, _Period, {period}, PRICE_CLOSE);
double rsi[];
CopyBuffer(handle_rsi, 0, 0, 10, rsi);
ArraySetAsSeries(rsi, true);
bool buy_signal = rsi[0] < {buy};
bool sell_signal = rsi[0] > {sell};
""",
            "python_snippet": """
df['rsi'] = df.ta.rsi(length={period})
buy_signal = df['rsi'].iloc[-1] < {buy}
sell_signal = df['rsi'].iloc[-1] > {sell}
""",
            "ui_flags": {
                "supports_divergence": True,
                "supports_levels": True,
                "default_visible": True,
            }
        },
        {
            "name": "Moving Average",
            "category": "trend",
            "description": "Simple/Exponential Moving Average - Identifies trend direction with slope confirmation",
            "parameters": {
                "period": 50,
                "type": "SMA",  # 'SMA' or 'EMA'
                "slope_confirmation": False,
            },
            "mql5_snippet": """
int handle_ma = iMA(_Symbol, _Period, {period}, 0, MODE_{type}, PRICE_CLOSE);
double ma[];
CopyBuffer(handle_ma, 0, 0, 5, ma);
ArraySetAsSeries(ma, true);
bool buy_signal = SymbolInfoDouble(_Symbol, SYMBOL_ASK) > ma[0];
bool sell_signal = SymbolInfoDouble(_Symbol, SYMBOL_BID) < ma[0];
""",
            "python_snippet": """
df['ma'] = df.ta.{type.lower()}(length={period})
buy_signal = df['close'].iloc[-1] > df['ma'].iloc[-1]
sell_signal = df['close'].iloc[-1] < df['ma'].iloc[-1]
""",
            "ui_flags": {
                "supports_slope": True,
                "supports_multiple_types": True,
                "default_visible": True,
            }
        },
        {
            "name": "MACD",
            "category": "trend",
            "description": "Moving Average Convergence Divergence - Trend-following momentum indicator",
            "parameters": {
                "fast": 12,
                "slow": 26,
                "signal": 9,
            },
            "mql5_snippet": """
int handle_macd = iMACD(_Symbol, _Period, {fast}, {slow}, {signal}, PRICE_CLOSE);
double main[], signal[];
CopyBuffer(handle_macd, 0, 0, 2, main);
CopyBuffer(handle_macd, 1, 0, 2, signal);
ArraySetAsSeries(main, true);
ArraySetAsSeries(signal, true);
bool buy_signal = main[0] > signal[0] && main[1] <= signal[1];
bool sell_signal = main[0] < signal[0] && main[1] >= signal[1];
""",
            "python_snippet": """
macd = df.ta.macd(fast={fast}, slow={slow}, signal={signal})
df = pd.concat([df, macd], axis=1)
buy_signal = df.iloc[-1]['MACD_{fast}_{slow}_{signal}'] > df.iloc[-1]['MACDs_{fast}_{slow}_{signal}']
sell_signal = df.iloc[-1]['MACD_{fast}_{slow}_{signal}'] < df.iloc[-1]['MACDs_{fast}_{slow}_{signal}']
""",
            "ui_flags": {
                "supports_histogram": True,
                "supports_crossover": True,
                "default_visible": False,
            }
        },
        {
            "name": "Bollinger Bands",
            "category": "volatility",
            "description": "Bollinger Bands - Volatility indicator with squeeze detection",
            "parameters": {
                "period": 20,
                "deviation": 2.0,
                "squeeze_detection": False,
            },
            "mql5_snippet": """
int handle_bands = iBands(_Symbol, _Period, {period}, 0, {deviation}, PRICE_CLOSE);
double upper[], lower[], middle[];
CopyBuffer(handle_bands, 0, 0, 5, middle);
CopyBuffer(handle_bands, 1, 0, 5, upper);
CopyBuffer(handle_bands, 2, 0, 5, lower);
ArraySetAsSeries(upper, true);
ArraySetAsSeries(lower, true);
bool buy_signal = SymbolInfoDouble(_Symbol, SYMBOL_ASK) < lower[0];
bool sell_signal = SymbolInfoDouble(_Symbol, SYMBOL_BID) > upper[0];
""",
            "python_snippet": """
bands = df.ta.bbands(length={period}, std={deviation})
df = pd.concat([df, bands], axis=1)
buy_signal = df['close'].iloc[-1] < df.iloc[-1]['BBL_{period}_{deviation}']
sell_signal = df['close'].iloc[-1] > df.iloc[-1]['BBU_{period}_{deviation}']
""",
            "ui_flags": {
                "supports_squeeze": True,
                "supports_width": True,
                "default_visible": False,
            }
        },
        {
            "name": "Stochastic",
            "category": "oscillator",
            "description": "Stochastic Oscillator - Momentum indicator comparing closing price to price range",
            "parameters": {
                "k_period": 5,
                "d_period": 3,
                "slowing": 3,
                "overbought": 80,
                "oversold": 20,
            },
            "mql5_snippet": """
int handle_stoch = iStochastic(_Symbol, _Period, {k_period}, {d_period}, {slowing}, MODE_SMA, STO_LOWHIGH);
double main_stoch[], signal_stoch[];
CopyBuffer(handle_stoch, 0, 0, 2, main_stoch);
CopyBuffer(handle_stoch, 1, 0, 2, signal_stoch);
ArraySetAsSeries(main_stoch, true);
ArraySetAsSeries(signal_stoch, true);
bool buy_signal = main_stoch[0] < {oversold} && main_stoch[0] > signal_stoch[0];
bool sell_signal = main_stoch[0] > {overbought} && main_stoch[0] < signal_stoch[0];
""",
            "python_snippet": """
stoch = df.ta.stoch(k={k_period}, d={d_period}, smooth_k={slowing})
df = pd.concat([df, stoch], axis=1)
buy_signal = df.iloc[-1]['STOCHk_{k_period}_{d_period}_{slowing}'] < {oversold}
sell_signal = df.iloc[-1]['STOCHk_{k_period}_{d_period}_{slowing}'] > {overbought}
""",
            "ui_flags": {
                "supports_levels": True,
                "supports_crossover": True,
                "default_visible": False,
            }
        },
        {
            "name": "ATR",
            "category": "volatility",
            "description": "Average True Range - Measures market volatility",
            "parameters": {
                "period": 14,
            },
            "mql5_snippet": """
int handle_atr = iATR(_Symbol, _Period, {period});
double atr[];
CopyBuffer(handle_atr, 0, 0, 1, atr);
double current_atr = atr[0];
""",
            "python_snippet": """
df['atr'] = df.ta.atr(length={period})
current_atr = df['atr'].iloc[-1]
""",
            "ui_flags": {
                "supports_stop_loss": True,
                "supports_position_sizing": True,
                "default_visible": False,
            }
        },
        {
            "name": "ADX",
            "category": "trend",
            "description": "Average Directional Index - Measures trend strength",
            "parameters": {
                "period": 14,
                "threshold": 25,
            },
            "mql5_snippet": """
int handle_adx = iADX(_Symbol, _Period, {period});
double adx[];
CopyBuffer(handle_adx, 0, 0, 1, adx);
bool strong_trend = adx[0] > {threshold};
""",
            "python_snippet": """
adx = df.ta.adx(length={period})
df = pd.concat([df, adx], axis=1)
strong_trend = df.iloc[-1]['ADX_{period}'] > {threshold}
""",
            "ui_flags": {
                "supports_trend_strength": True,
                "default_visible": False,
            }
        },
        {
            "name": "EMA Crossover",
            "category": "trend",
            "description": "Exponential Moving Average Crossover - Fast/Slow EMA cross strategy",
            "parameters": {
                "fast_period": 12,
                "slow_period": 26,
            },
            "mql5_snippet": """
int handle_ema_fast = iMA(_Symbol, _Period, {fast_period}, 0, MODE_EMA, PRICE_CLOSE);
int handle_ema_slow = iMA(_Symbol, _Period, {slow_period}, 0, MODE_EMA, PRICE_CLOSE);
double ema_fast[], ema_slow[];
CopyBuffer(handle_ema_fast, 0, 0, 2, ema_fast);
CopyBuffer(handle_ema_slow, 0, 0, 2, ema_slow);
ArraySetAsSeries(ema_fast, true);
ArraySetAsSeries(ema_slow, true);
bool buy_signal = ema_fast[0] > ema_slow[0] && ema_fast[1] <= ema_slow[1];
bool sell_signal = ema_fast[0] < ema_slow[0] && ema_fast[1] >= ema_slow[1];
""",
            "python_snippet": """
df['ema_fast'] = df.ta.ema(length={fast_period})
df['ema_slow'] = df.ta.ema(length={slow_period})
buy_signal = df['ema_fast'].iloc[-1] > df['ema_slow'].iloc[-1] and df['ema_fast'].iloc[-2] <= df['ema_slow'].iloc[-2]
sell_signal = df['ema_fast'].iloc[-1] < df['ema_slow'].iloc[-1] and df['ema_fast'].iloc[-2] >= df['ema_slow'].iloc[-2]
""",
            "ui_flags": {
                "supports_crossover": True,
                "supports_multiple_periods": True,
                "default_visible": False,
            }
        },
    ]
    
    created_count = 0
    updated_count = 0
    
    for indicator_data in indicators:
        indicator, created = IndicatorTemplate.objects.update_or_create(
            name=indicator_data["name"],
            defaults=indicator_data
        )
        if created:
            created_count += 1
            print(f"✓ Created: {indicator.name}")
        else:
            updated_count += 1
            print(f"↻ Updated: {indicator.name}")
    
    print(f"\n{'='*50}")
    print(f"Seeding complete!")
    print(f"Created: {created_count} indicators")
    print(f"Updated: {updated_count} indicators")
    print(f"Total: {IndicatorTemplate.objects.count()} indicators in database")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("Seeding Indicator Templates...")
    print("="*50 + "\n")
    seed_indicators()
