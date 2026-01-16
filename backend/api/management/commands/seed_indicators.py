"""
Django management command to seed indicator templates
Run with: python manage.py seed_indicators
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from api.models import IndicatorTemplate


class Command(BaseCommand):
    help = 'Seeds the database with indicator templates'

    @transaction.non_atomic_requests
    def handle(self, *args, **options):
        self.stdout.write("\n" + "="*50)
        self.stdout.write("Seeding Indicator Templates...")
        self.stdout.write("="*50 + "\n")
        
        indicators = [
            {
                "name": "RSI",
                "category": "oscillator",
                "description": "Relative Strength Index - Measures momentum with overbought/oversold levels and divergence detection",
                "parameters": {
                    "period": 14,
                    "buy": 30,
                    "sell": 70,
                    "mode": "level",
                },
                "mql5_snippet": "int handle_rsi = iRSI(_Symbol, _Period, {period}, PRICE_CLOSE);",
                "python_snippet": "df['rsi'] = df.ta.rsi(length={period})",
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
                    "type": "SMA",
                    "slope_confirmation": False,
                },
                "mql5_snippet": "int handle_ma = iMA(_Symbol, _Period, {period}, 0, MODE_{type}, PRICE_CLOSE);",
                "python_snippet": "df['ma'] = df.ta.{type.lower()}(length={period})",
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
                "mql5_snippet": "int handle_macd = iMACD(_Symbol, _Period, {fast}, {slow}, {signal}, PRICE_CLOSE);",
                "python_snippet": "macd = df.ta.macd(fast={fast}, slow={slow}, signal={signal})",
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
                "mql5_snippet": "int handle_bands = iBands(_Symbol, _Period, {period}, 0, {deviation}, PRICE_CLOSE);",
                "python_snippet": "bands = df.ta.bbands(length={period}, std={deviation})",
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
                "mql5_snippet": "int handle_stoch = iStochastic(_Symbol, _Period, {k_period}, {d_period}, {slowing}, MODE_SMA, STO_LOWHIGH);",
                "python_snippet": "stoch = df.ta.stoch(k={k_period}, d={d_period}, smooth_k={slowing})",
                "ui_flags": {
                    "supports_levels": True,
                    "supports_crossover": True,
                    "default_visible": False,
                }
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for indicator_data in indicators:
            try:
                # Try to get existing
                indicator = IndicatorTemplate.objects.filter(name=indicator_data["name"]).first()
                if indicator:
                    # Update existing
                    for key, value in indicator_data.items():
                        setattr(indicator, key, value)
                    indicator.save()
                    updated_count += 1
                    self.stdout.write(self.style.WARNING(f"[UPDATED] {indicator.name}"))
                else:
                    # Create new
                    indicator = IndicatorTemplate.objects.create(**indicator_data)
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f"[CREATED] {indicator.name}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"[ERROR] {indicator_data['name']}: {str(e)}"))
        
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS(f"Seeding complete!"))
        self.stdout.write(f"Created: {created_count} indicators")
        self.stdout.write(f"Updated: {updated_count} indicators")
        self.stdout.write(f"Total: {IndicatorTemplate.objects.count()} indicators in database")
        self.stdout.write("="*50 + "\n")
