from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLES = [
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('user', 'User'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    avatar_url = models.URLField(blank=True)
    role = models.CharField(max_length=20, choices=ROLES, default='user')
    trading_permissions = models.JSONField(default=dict) # e.g. {"can_create_robots": True}
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile of {self.user.username} ({self.role})"

class TradingAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trading_accounts')
    account_number = models.CharField(max_length=50)
    password = models.CharField(max_length=255, blank=True, null=True)  # Encrypted
    server = models.CharField(max_length=100, blank=True, null=True)    # Encrypted
    mode = models.CharField(max_length=20, choices=[('demo', 'Demo'), ('live', 'Live')])
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    equity = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    lot_size = models.FloatField(default=0.01)
    status = models.CharField(max_length=20, default='active') # active, disabled, etc.
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.account_number} ({self.mode})"

class Robot(models.Model):
    METHODS = [
        ('winrate', 'Indicator Win-Rate'),
        ('ml', 'RNN Machine Learning'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='robots')
    symbol = models.CharField(max_length=20)
    method = models.CharField(max_length=20, choices=METHODS)
    indicators = models.JSONField(default=list)
    risk_settings = models.JSONField(default=dict) # {lot: 0.01, sl: 30, tp: 60}
    win_rate = models.FloatField(default=0.0)
    mql5_code = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.symbol} - {self.method} ({self.user.username})"

class AppVisit(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    page_visited = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.page_visited} at {self.timestamp}"

class TradeLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    robot = models.ForeignKey(Robot, on_delete=models.CASCADE, null=True, blank=True)
    symbol = models.CharField(max_length=20)
    action = models.CharField(max_length=10) # BUY/SELL
    price = models.FloatField()
    profit = models.FloatField(default=0.0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} {self.symbol} by {self.user.username}"
