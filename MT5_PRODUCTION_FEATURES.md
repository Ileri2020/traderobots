# MT5 Production Features - Implementation Guide

## Overview

This document explains the three critical production features now implemented in your trading platform:

1. **EA Injection Confirmation** - Guarantees EAs are loaded and running
2. **MT5 Watchdog Service** - Self-healing MT5 connection monitoring
3. **Per-User MT5 Isolation** - Safe multi-user trading environment

---

## 1. EA Injection Confirmation

### What It Does

Provides **authoritative confirmation** that an EA is:

- ✅ Successfully loaded into MT5
- ✅ Initialized without errors
- ✅ Actively running and communicating

### How It Works

#### MQL5 Side (EA Code)

Every generated EA now includes:

```mql5
// Global variable signals
GlobalVariableSet("EA_READY_" + RobotId, TimeCurrent());
GlobalVariableSet("EA_HEARTBEAT_" + RobotId, TimeCurrent());

// Heartbeat file
FileWrite(handle, TimeToString(TimeCurrent()));
```

#### Python Side (Backend)

```python
from trading.ea_manager import EAManager

# Deploy and wait for confirmation
result = EAManager.deploy_and_confirm(
    robot_id=robot.id,
    symbol="EURUSD",
    timeframe="H1",
    timeout=60
)

# Result contains:
# - ready_confirmed: bool
# - heartbeat_confirmed: bool
# - chart_opened: bool
# - status: "SUCCESS" | "PARTIAL" | "FAILED"
```

### API Endpoints

**Check EA Status:**

```http
GET /api/accounts/ea/status/{robot_id}/
```

Response:

```json
{
  "robot_id": 123,
  "ready": true,
  "heartbeat_active": true,
  "heartbeat_age": 2.5,
  "errors": []
}
```

### Usage in Deployment

The EA Manager is automatically used during robot deployment (Phase 3):

```python
# In views.py - deploy() method
deployment_result = EAManager.deploy_and_confirm(
    robot_id=robot.id,
    symbol=robot.symbol,
    timeframe="H1",
    timeout=60
)
```

---

## 2. MT5 Watchdog Service

### What It Does

Continuously monitors MT5 health and **automatically recovers** from:

- ❌ MT5 terminal crashes
- ❌ IPC connection failures
- ❌ Lost broker connections
- ❌ EA freezes

### How It Works

#### Monitoring Checks (Every 10 seconds)

1. **Process Check** - Is MT5 terminal running?
2. **IPC Check** - Can Python communicate with MT5?
3. **Account Check** - Is account authorized?
4. **EA Heartbeat** - Is EA still alive?

#### Auto-Recovery Actions

- **Terminal Down** → Restart MT5
- **IPC Dead** → Reinitialize connection
- **Account Disconnected** → Re-login
- **EA Stale** → Alert (requires manual redeploy)

### Usage

#### Start Watchdog

```python
from trading.mt5_watchdog import MT5Watchdog

watchdog = MT5Watchdog(
    mt5_path=r"C:\Program Files\MetaTrader 5\terminal64.exe",
    login=100690024,
    password="your_password",
    server="XMGlobal-MT5 5",
    check_interval=10
)

# Start monitoring
watchdog.start(robot_id=123)  # Optional: monitor specific robot
```

#### API Endpoint

```http
POST /api/accounts/mt5/start-watchdog/
Content-Type: application/json

{
  "robot_id": 123
}
```

Response:

```json
{
  "status": "WATCHDOG_STARTED",
  "robot_id": 123,
  "check_interval": 10
}
```

### Watchdog Logs

Monitor watchdog activity in your Django logs:

```
INFO: MT5 Watchdog started
WARNING: MT5 terminal not running
INFO: Starting MT5 terminal...
INFO: MT5 connection recovered successfully. Account: 100690024
WARNING: EA heartbeat stale for robot 123
```

---

## 3. Per-User MT5 Isolation

### What It Does

Provides **isolated MT5 environments** for each user:

- ✅ Separate data directories
- ✅ Separate EA folders
- ✅ Separate terminal instances
- ✅ No cross-account contamination

### Why It's Critical

**Without isolation:**

- ❌ One user's EA can affect another's trades
- ❌ One crash kills all users
- ❌ Account credentials can leak
- ❌ Broker compliance issues

**With isolation:**

- ✅ Each user has their own MT5
- ✅ Safe scaling to 100+ users
- ✅ Broker-compliant architecture
- ✅ Crash-resistant

### Directory Structure

```
C:\mt5_users\
├── user_1\
│   ├── MQL5\
│   │   ├── Experts\
│   │   │   └── Robot_123.mq5
│   │   └── Files\
│   │       └── heartbeat_123.txt
│   └── Logs\
├── user_2\
│   ├── MQL5\
│   └── Logs\
└── user_3\
    ├── MQL5\
    └── Logs\
```

### Usage

#### Initialize User MT5

```python
from trading.user_mt5_manager import UserMT5Manager

# Create user-specific MT5 manager
user_mt5 = UserMT5Manager(
    user_id=request.user.id,
    login=account.account_number,
    password=decrypt_value(account.password),
    server=decrypt_value(account.server)
)

# Connect (auto-launches isolated terminal)
user_mt5.connect()

# Deploy EA to user's directory
ea_path = user_mt5.deploy_ea(robot_id=123, ea_code=mql5_code)
```

#### Get User Stats

```python
stats = user_mt5.get_user_stats()
# Returns:
# {
#   "user_id": 1,
#   "user_dir": "C:/mt5_users/user_1",
#   "dir_exists": True,
#   "ea_count": 5,
#   "log_files": 12
# }
```

#### System-Wide Stats

```python
system_stats = UserMT5Manager.get_system_stats()
# Returns:
# {
#   "total_users": 10,
#   "total_eas": 47,
#   "base_dir": "C:/mt5_users",
#   "base_dir_exists": True
# }
```

---

## Integration Checklist

### For Robot Creation

- [x] EA code includes heartbeat logic
- [x] Robot ID passed to `generate_mql5()`
- [x] EA Manager used for deployment confirmation

### For Deployment

- [x] Phase 3 uses `EAManager.deploy_and_confirm()`
- [x] Deployment validation stores confirmation status
- [x] Frontend displays confirmation results

### For Production

- [ ] Start watchdog on server startup
- [ ] Enable per-user isolation for multi-user deployments
- [ ] Monitor watchdog logs
- [ ] Set up alerts for consecutive failures

---

## API Reference

### EA Management

```http
GET /api/accounts/ea/status/{robot_id}/
```

### Watchdog Control

```http
POST /api/accounts/mt5/start-watchdog/
Body: {"robot_id": 123}
```

### MT5 Health

```http
GET /api/accounts/mt5/status/
POST /api/accounts/mt5/reconnect/
```

---

## Troubleshooting

### EA Not Confirming

**Symptom:** `EA_READY` signal not detected

**Solutions:**

1. Check EA compiled successfully
2. Verify EA attached to chart
3. Check MT5 terminal logs
4. Ensure "Allow Algorithmic Trading" is enabled

### Watchdog Not Recovering

**Symptom:** Consecutive recovery failures

**Solutions:**

1. Check MT5 credentials are correct
2. Verify MT5 terminal path
3. Ensure MT5 has been logged in manually at least once
4. Check Windows permissions

### User Isolation Not Working

**Symptom:** Users seeing each other's EAs

**Solutions:**

1. Verify `C:\mt5_users\` directory exists
2. Check MT5 launched with `/portable` flag
3. Ensure each user has unique data directory
4. Restart MT5 terminals

---

## Performance Considerations

### Watchdog

- **CPU Impact:** Minimal (~0.1% per check)
- **Memory:** ~5MB per watchdog instance
- **Recommended:** 1 watchdog per server (monitors all robots)

### User Isolation

- **Disk Space:** ~50MB per user (MT5 data directory)
- **Memory:** ~100MB per MT5 instance
- **Recommended:** Max 10 concurrent MT5 instances per server

---

## Security Notes

1. **Credentials:** Never log passwords in watchdog
2. **File Permissions:** Restrict `C:\mt5_users\` to service account
3. **Heartbeat Files:** Regularly clean old heartbeat files
4. **Global Variables:** MT5 global variables are terminal-wide (not isolated)

---

## Next Steps

1. **Test EA Confirmation:**

   - Create a robot
   - Deploy it
   - Check `/api/accounts/ea/status/{robot_id}/`

2. **Enable Watchdog:**

   - Start watchdog on server boot
   - Monitor logs for 24 hours
   - Verify auto-recovery works

3. **Plan User Isolation:**
   - Estimate concurrent users
   - Calculate resource requirements
   - Set up monitoring

---

## Support

For issues or questions:

1. Check Django logs: `backend/logs/`
2. Check MT5 logs: `C:\mt5_users\user_{id}\Logs\`
3. Review watchdog output
4. Verify EA heartbeat files exist
