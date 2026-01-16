# MT5 Path Configuration Update - Summary

## Changes Made

This document summarizes all changes made to fix MT5 initialization across the entire application to use the XM Global MT5 installation path.

### Files Modified:

1. **`.env`** (Created)

   - Added `MT5_PATH=C:\Program Files\XM Global MT5\terminal64.exe`
   - This environment variable is now the single source of truth for the MT5 installation path

2. **`backend/trading/mt5_connector.py`**

   - Updated `DEFAULT_PATH` to use XM Global MT5 path
   - Changed from: `r"C:\Program Files\MetaTrader 5\terminal64.exe"`
   - Changed to: `os.getenv("MT5_PATH", r"C:\Program Files\XM Global MT5\terminal64.exe")`

3. **`backend/trading/user_mt5_manager.py`**

   - Updated `MT5_EXECUTABLE` to use environment variable
   - Changed from: `r"C:\Program Files\MetaTrader 5\terminal64.exe"`
   - Changed to: `os.getenv("MT5_PATH", r"C:\Program Files\XM Global MT5\terminal64.exe")`

4. **`backend/trading/mt5_watchdog.py`**

   - No changes needed (already takes path as parameter in `__init__`)

5. **`backend/api/views.py`**

   - Updated `start_watchdog` method to use XM Global MT5 path
   - Changed default path in watchdog initialization

6. **`diagnose_mt5.py`**

   - Updated to use environment variable for MT5 path
   - Added explicit path parameter to `mt5.initialize()`
   - Now shows which path is being used during initialization

7. **`backend/test_mt5_connection.py`**

   - Updated `MT5_PATH` to use environment variable
   - Updated initialization call to include path parameter

8. **`backend/trading/robot_generator.py`**
   - Updated generated Python code to include MT5_PATH constant
   - Modified `connect()` function to use path parameter in `mt5.initialize()`
   - Generated code now checks environment variable first, then falls back to XM Global path

## How It Works

The application now follows this hierarchy for determining the MT5 path:

1. **Environment Variable** (`.env` file): `MT5_PATH=C:\Program Files\XM Global MT5\terminal64.exe`
2. **Fallback Default**: If environment variable is not set, uses `C:\Program Files\XM Global MT5\terminal64.exe`

## Testing

To verify the changes work correctly:

1. **Test MT5 Connection:**

   ```bash
   cd backend
   python test_mt5_connection.py
   ```

2. **Test Diagnostic Script:**

   ```bash
   python diagnose_mt5.py
   ```

3. **Verify Environment Variable:**
   - Check that `.env` file exists in project root
   - Verify `MT5_PATH` is set correctly

## Important Notes

- All MT5 initialization calls now include the `path` parameter
- The XM Global MT5 terminal must be installed at: `C:\Program Files\XM Global MT5\terminal64.exe`
- If you need to use a different path, update the `MT5_PATH` in the `.env` file
- Generated robot code will also respect the environment variable

## Next Steps

1. Restart any running Django servers to pick up the new environment variable
2. Test MT5 connection using the diagnostic scripts
3. Verify robot creation and deployment workflows work correctly
