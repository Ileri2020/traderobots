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
    preferred_broker = models.CharField(max_length=100, blank=True)
    trading_permissions = models.JSONField(default=dict) # e.g. {"can_create_robots": True}
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile of {self.user.username} ({self.role})"

class TradingAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mt5_accounts")

    broker = models.CharField(max_length=100)
    mt5_login = models.CharField(max_length=20)

    # ENCRYPTED
    mt5_password = models.BinaryField()
    mt5_server = models.CharField(max_length=100)

    is_demo = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.mt5_login}"

class Robot(models.Model):
    METHODS = [
        ('winrate', 'Indicator Win-Rate'),
        ('ml', 'RNN Machine Learning'),
    ]
    STRATEGY_CLASSES = [
        ('RULE', 'Rule-Based Strategy'),
        ('OPTIMIZED_RULE', 'Optimized Rule Strategy'),
        ('ML', 'Machine-Learning Strategy'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='robots')
    name = models.CharField(max_length=100, default='Unnamed Robot')
    symbol = models.CharField(max_length=20)
    method = models.CharField(max_length=20, choices=METHODS)
    strategy_class = models.CharField(max_length=20, choices=STRATEGY_CLASSES, default='RULE')
    indicators = models.JSONField(default=list)
    risk_settings = models.JSONField(default=dict) # {lot: 0.01, sl: 30, tp: 60, max_daily_loss: 5, max_concurrent: 3}
    win_rate = models.FloatField(default=0.0)
    mql5_code = models.TextField(blank=True, null=True)
    python_code = models.TextField(blank=True, null=True)
    version = models.IntegerField(default=1)
    is_active = models.BooleanField(default=False)

    # Historical Analysis & Execution Config
    LOOKBACK_CHOICES = [
        (1, '1 Month'), (3, '3 Months'), (6, '6 Months'), (12, '1 Year'), (24, '2 Years')
    ]
    SESSION_CHOICES = [
        ('ANY', 'Any Session'), ('LONDON', 'London'), ('NY', 'New York'), ('ASIA', 'Asia')
    ]
    
    historical_lookback = models.IntegerField(choices=LOOKBACK_CHOICES, default=3)
    recency_bias = models.FloatField(default=0.1, help_text="Lambda value for time weighting")
    session_preference = models.CharField(max_length=10, choices=SESSION_CHOICES, default='ANY')
    confidence_threshold = models.FloatField(default=0.6)
    max_entry_wait_minutes = models.IntegerField(default=60)
    
    # Data Provenance
    DATA_SOURCE_CHOICES = [
        ('MT5', 'MetaTrader 5'), 
        ('YFINANCE', 'Yahoo Finance'), 
        ('MIXED', 'Mixed Sources'),
        ('NONE', 'Not Trained')
    ]
    training_data_source = models.CharField(max_length=20, choices=DATA_SOURCE_CHOICES, default='NONE')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.symbol} - {self.method} V{self.version} ({self.user.username})"

class RobotBuildReport(models.Model):
    """
    Persistent record of a robot's build quality and data integrity.
    No robot is deployable unless the latest report is SUCCESS.
    """
    STATUS_CHOICES = [
        ('SUCCESS', 'Success'),
        ('PARTIAL', 'Partial Success (Warnings)'),
        ('FAILED', 'Failed'),
    ]
    DATA_SOURCE_CHOICES = [
        ('MT5', 'MetaTrader 5'),
        ('YFINANCE', 'Yahoo Finance'),
        ('MIXED', 'Mixed Sources'),
    ]
    
    robot = models.ForeignKey(Robot, on_delete=models.CASCADE, related_name='build_reports')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    data_source = models.CharField(max_length=20, choices=DATA_SOURCE_CHOICES)
    candle_count = models.IntegerField(default=0)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    errors = models.JSONField(default=list)   # List of structured error objects
    warnings = models.JSONField(default=list) # List of structured warning objects
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

class RobotBuildTask(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('BUILDING', 'Building'),
        ('FAILED', 'Failed'),
        ('COMPLETE', 'Complete'),
    ]
    robot = models.ForeignKey(Robot, on_delete=models.CASCADE, related_name='build_tasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    progress = models.IntegerField(default=0)
    log = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class StrategyVersion(models.Model):
    robot = models.ForeignKey(Robot, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField()
    indicators = models.JSONField()
    risk_settings = models.JSONField()
    mql5_code = models.TextField(blank=True, null=True)
    python_code = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('robot', 'version_number')

class AppVisit(models.Model):
    ip_address = models.CharField(max_length=45)
    visit_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.ip_address} at {self.visit_time}"

class TradeLog(models.Model):
    STATUS_CHOICES = [
        ('IDLE', 'Idle'),
        ('ANALYZING', 'Analyzing History'),
        ('ORDER_PLACED', 'Conditional Order Placed'),
        ('TRIGGERED', 'Order Triggered'),
        ('CLOSED', 'Trade Closed'),
        ('EXPIRED', 'Order Expired'),
        ('FAILED', 'Failed'),
    ]
    ENTRY_TYPE_CHOICES = [
        ('MARKET', 'Market'),
        ('BUY_LIMIT', 'Buy Limit'), ('SELL_LIMIT', 'Sell Limit'),
        ('BUY_STOP', 'Buy Stop'), ('SELL_STOP', 'Sell Stop')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    robot = models.ForeignKey(Robot, on_delete=models.CASCADE, related_name='trades')
    symbol = models.CharField(max_length=10)
    action = models.CharField(max_length=10)  # BUY/SELL (Legacy)
    
    # State Machine & Execution details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IDLE')
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPE_CHOICES, default='MARKET')
    confidence_score = models.FloatField(default=0.0)
    
    # Prices
    price = models.FloatField()  # Actual execution price
    target_entry = models.FloatField(null=True, blank=True) # Desired conditional price
    sl = models.FloatField(null=True, blank=True)
    tp = models.FloatField(null=True, blank=True)
    
    # Outcomes
    profit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Balance Tracking
    initial_balance = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    final_balance = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Metrics
    latency = models.FloatField(null=True, blank=True, help_text="Execution latency in ms")
    slippage = models.FloatField(null=True, blank=True, help_text="Slippage in pips")
    spread = models.FloatField(null=True, blank=True)
    failure_reason = models.TextField(blank=True)
    
    # Timings
    timestamp = models.DateTimeField(auto_now_add=True) # Creation time
    triggered_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    expiry_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.action} {self.symbol} by {self.user.username}"

class AccountGuardrail(models.Model):
    """Account-level risk management guardrails"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='guardrails')
    max_daily_loss = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    max_concurrent_positions = models.IntegerField(default=3)
    max_correlation_exposure = models.FloatField(default=0.7)  # 0-1 scale
    daily_loss_current = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    last_reset = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Guardrails for {self.user.username}"

class EmergencyKillSwitch(models.Model):
    """Emergency kill switch for stopping all trading activity"""
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('TRIGGERED', 'Triggered'),
        ('RESOLVED', 'Resolved'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='kill_switches')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    triggered_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    reason = models.TextField(blank=True)
    close_positions = models.BooleanField(default=False)
    revoke_mt5_access = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Kill Switch - {self.user.username} ({self.status})"

class DeploymentValidation(models.Model):
    """Track deployment validation phases"""
    PHASE_CHOICES = [
        ('PREFLIGHT', 'Preflight Validation'),
        ('INJECTION', 'Code Injection'),
        ('CONFIRMATION', 'Execution Confirmation'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]
    robot = models.ForeignKey(Robot, on_delete=models.CASCADE, related_name='deployment_validations')
    phase = models.CharField(max_length=20, choices=PHASE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    message = models.TextField(blank=True)
    mt5_terminal_reachable = models.BooleanField(default=False)
    account_authorized = models.BooleanField(default=False)
    symbol_exists = models.BooleanField(default=False)
    lot_size_allowed = models.BooleanField(default=False)
    ea_attached = models.BooleanField(default=False)
    heartbeat_received = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Deployment {self.phase} - {self.robot.name} ({self.status})"

class IndicatorTemplate(models.Model):
    """Registry of indicator templates with code snippets"""
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50)  # e.g., 'oscillator', 'trend', 'volume'
    description = models.TextField()
    parameters = models.JSONField(default=dict)  # Available parameters and defaults
    mql5_snippet = models.TextField()  # MQL5 code template
    python_snippet = models.TextField()  # Python code template
    ui_flags = models.JSONField(default=dict)  # UI configuration flags
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.category})"

class RobotEvent(models.Model):
    """Unified event timeline for robots"""
    EVENT_TYPES = [
        ('CREATED', 'Created'),
        ('DEPLOYED', 'Deployed'),
        ('TRADE_EXECUTED', 'Trade Executed'),
        ('ERROR', 'Error'),
        ('STOPPED', 'Stopped'),
        ('UPDATED', 'Updated'),
    ]
    robot = models.ForeignKey(Robot, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    description = models.TextField()
    metadata = models.JSONField(default=dict)  # Additional event data
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.robot.name} - {self.event_type} at {self.timestamp}"
