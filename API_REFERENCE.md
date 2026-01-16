# Traderobots API Quick Reference

## Base URL

```
Development: http://localhost:8000/api
Production: https://your-domain.com/api
```

## Authentication

All endpoints except login/register require authentication.

```javascript
headers: {
  'Authorization': 'Token YOUR_AUTH_TOKEN',
  'Content-Type': 'application/json'
}
```

## Endpoints

### 🤖 Robots

#### Create Win-Rate Robot

```http
POST /api/robots/create_winrate_robot/
```

**Body:**

```json
{
  "name": "My Trading Bot",
  "symbol": "EURUSD",
  "timeframe": "H1",
  "strategy_class": "RULE",
  "indicators": ["rsi", "ma"],
  "risk": {
    "lot": 0.01,
    "sl": 30,
    "tp": 60
  },
  "rsi_settings": {
    "period": 14,
    "buy": 30,
    "sell": 70,
    "mode": "level"
  },
  "ma_settings": {
    "period": 50,
    "type": "MODE_SMA",
    "slope_confirmation": false
  }
}
```

**Response:**

```json
{
  "robot": { "id": 1, "name": "My Trading Bot", ... },
  "task_id": 123
}
```

#### Create RNN Robot

```http
POST /api/robots/create_rnn_robot/
```

**Body:**

```json
{
  "name": "ML Bot EURUSD",
  "symbol": "EURUSD",
  "years": 2
}
```

#### Deploy Robot

```http
POST /api/robots/{id}/deploy/
```

**Body:**

```json
{
  "account_id": 1,
  "risk": {
    "lot": 0.01,
    "sl": 30,
    "tp": 60
  }
}
```

**Response:**

```json
{
  "status": "deployed",
  "phases": [
    {"name": "Preflight", "status": "SUCCESS", "id": 1},
    {"name": "Injection", "status": "SUCCESS", "id": 2},
    {"name": "Confirmation", "status": "SUCCESS", "id": 3}
  ],
  "robot": { ... }
}
```

#### Stop Robot

```http
POST /api/robots/{id}/stop/
```

#### Get Event Timeline

```http
GET /api/robots/{id}/events/
```

**Response:**

```json
[
  {
    "id": 1,
    "event_type": "CREATED",
    "description": "Robot My Trading Bot created with RULE strategy",
    "metadata": {"indicators": ["rsi", "ma"], "risk": {...}},
    "timestamp": "2026-01-09T10:30:00Z"
  },
  {
    "id": 2,
    "event_type": "DEPLOYED",
    "description": "Robot deployed to account 12345",
    "metadata": {"account_id": 1, ...},
    "timestamp": "2026-01-09T10:35:00Z"
  }
]
```

#### Get Version History

```http
GET /api/robots/{id}/versions/
```

#### Rollback to Version

```http
POST /api/robots/{id}/rollback/
```

**Body:**

```json
{
  "version_number": 2
}
```

#### Risk Simulation

```http
POST /api/robots/risk_simulate/
```

**Body:**

```json
{
  "symbol": "EURUSD",
  "lot": 0.01,
  "sl": 30
}
```

**Response:**

```json
{
  "pip_value": "$0.10",
  "risk_amount": "$3.00",
  "margin_usage": "$10.00 (approx)",
  "drawdown_est": "2.4% (historical avg)"
}
```

### 📊 Build Tasks

#### Get Build Task Status

```http
GET /api/build-tasks/{id}/
```

**Response:**

```json
{
  "id": 123,
  "robot": 1,
  "status": "BUILDING",
  "progress": 45,
  "log": "Running backtest...",
  "created_at": "2026-01-09T10:30:00Z",
  "updated_at": "2026-01-09T10:30:15Z"
}
```

**Status Values:**

- `PENDING`: Task queued
- `BUILDING`: In progress
- `COMPLETE`: Successfully completed
- `FAILED`: Build failed

### 🛡️ Risk Management

#### Get Guardrails

```http
GET /api/guardrails/
```

**Response:**

```json
[
  {
    "id": 1,
    "user": 1,
    "max_daily_loss": "100.00",
    "max_concurrent_positions": 3,
    "max_correlation_exposure": 0.7,
    "daily_loss_current": "25.50",
    "is_active": true,
    "last_reset": "2026-01-09T00:00:00Z"
  }
]
```

#### Update Guardrails

```http
PATCH /api/guardrails/{id}/
```

**Body:**

```json
{
  "max_daily_loss": "150.00",
  "max_concurrent_positions": 5
}
```

#### Reset Daily Loss

```http
POST /api/guardrails/{id}/reset_daily_loss/
```

### 🚨 Emergency Kill Switch

#### Trigger Kill Switch

```http
POST /api/kill-switch/trigger/
```

**Body:**

```json
{
  "reason": "Market volatility too high",
  "close_positions": false,
  "revoke_mt5_access": false
}
```

**Response:**

```json
{
  "status": "triggered",
  "kill_switch": {
    "id": 1,
    "status": "TRIGGERED",
    "triggered_at": "2026-01-09T10:45:00Z",
    "reason": "Market volatility too high"
  },
  "robots_stopped": 5
}
```

#### Resolve Kill Switch

```http
POST /api/kill-switch/{id}/resolve/
```

### 📈 Indicator Templates

#### List All Indicators

```http
GET /api/indicator-templates/
```

**Response:**

```json
[
  {
    "id": 1,
    "name": "RSI",
    "category": "oscillator",
    "description": "Relative Strength Index - Measures momentum...",
    "parameters": {
      "period": 14,
      "buy": 30,
      "sell": 70,
      "mode": "level"
    },
    "ui_flags": {
      "supports_divergence": true,
      "supports_levels": true,
      "default_visible": true
    }
  }
]
```

#### Filter by Category

```http
GET /api/indicator-templates/by_category/?category=oscillator
```

**Categories:**

- `oscillator`: RSI, Stochastic
- `trend`: MA, MACD, ADX, EMA Crossover
- `volatility`: Bollinger Bands, ATR

### 📝 Trade Logs

#### Get Execution Quality

```http
GET /api/logs/execution_quality/
```

**Response:**

```json
{
  "avg_latency_ms": 45.23,
  "avg_slippage_pips": 0.8,
  "failure_rate": 2.5,
  "total_trades": 150
}
```

#### List Trade Logs

```http
GET /api/logs/
```

**Response:**

```json
[
  {
    "id": 1,
    "user": 1,
    "robot": 1,
    "symbol": "EURUSD",
    "action": "BUY",
    "price": 1.085,
    "profit": 15.5,
    "latency": 42.5,
    "slippage": 0.5,
    "spread": 1.2,
    "failure_reason": "",
    "timestamp": "2026-01-09T10:30:00Z"
  }
]
```

### 👤 User Management

#### Register

```http
POST /api/users/register/
```

**Body:**

```json
{
  "username": "trader123",
  "email": "trader@example.com",
  "password": "securepassword"
}
```

#### Login

```http
POST /api/users/login/
```

**Body:**

```json
{
  "username": "trader123",
  "password": "securepassword"
}
```

#### Google Login

```http
POST /api/users/google_login/
```

**Body:**

```json
{
  "email": "trader@gmail.com"
}
```

#### Logout

```http
POST /api/users/logout/
```

### 💼 Trading Accounts

#### Sync MT5 Account

```http
GET /api/accounts/sync/
```

**Response:**

```json
{
  "id": 1,
  "user": 1,
  "account_number": "12345",
  "balance": "10000.00",
  "equity": "10250.00",
  "mode": "demo",
  "status": "active"
}
```

## Error Responses

### 400 Bad Request

```json
{
  "error": "Invalid parameters",
  "details": "Symbol INVALID not supported"
}
```

### 401 Unauthorized

```json
{
  "error": "Authentication required"
}
```

### 403 Forbidden

```json
{
  "error": "Emergency kill switch is active. Cannot deploy robots.",
  "kill_switch_id": 1
}
```

### 404 Not Found

```json
{
  "error": "Robot not found"
}
```

### 503 Service Unavailable

```json
{
  "error": "MT5 Terminal unreachable",
  "phase": "PREFLIGHT",
  "validation_id": 1
}
```

## WebSocket Support (Future)

For real-time updates, consider implementing WebSocket connections:

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/build-tasks/123/");

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("Progress:", data.progress, "%");
  console.log("Log:", data.log);
};
```

## Rate Limiting

- **Anonymous**: 100 requests/hour
- **Authenticated**: 1000 requests/hour
- **Build Tasks**: 10 concurrent builds per user

## Best Practices

1. **Always poll build tasks** instead of using fake timers
2. **Check kill switch status** before deploying robots
3. **Monitor guardrails** to prevent account violations
4. **Use risk simulation** before deploying with real money
5. **Track event timeline** for debugging and auditing
6. **Implement retry logic** for failed deployments
7. **Cache indicator templates** to reduce API calls

## Example: Complete Robot Creation Flow

```javascript
// 1. Create robot
const createResponse = await fetch("/api/robots/create_winrate_robot/", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    name: "My Bot",
    symbol: "EURUSD",
    strategy_class: "RULE",
    indicators: ["rsi"],
    risk: { lot: 0.01, sl: 30, tp: 60 },
  }),
});

const { robot, task_id } = await createResponse.json();

// 2. Poll build progress
const pollInterval = setInterval(async () => {
  const taskResponse = await fetch(`/api/build-tasks/${task_id}/`);
  const task = await taskResponse.json();

  console.log(`Progress: ${task.progress}% - ${task.log}`);

  if (task.status === "COMPLETE") {
    clearInterval(pollInterval);
    console.log("Robot built successfully!");

    // 3. Deploy robot
    const deployResponse = await fetch(`/api/robots/${robot.id}/deploy/`, {
      method: "POST",
      body: JSON.stringify({
        account_id: 1,
        risk: { lot: 0.01, sl: 30, tp: 60 },
      }),
    });

    const deployment = await deployResponse.json();
    console.log("Deployment phases:", deployment.phases);
  } else if (task.status === "FAILED") {
    clearInterval(pollInterval);
    console.error("Build failed:", task.log);
  }
}, 1000);
```

---

**Last Updated**: 2026-01-09  
**API Version**: 1.0  
**Backend**: Django 3.2 + DRF
