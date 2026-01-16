"""
MT5 Watchdog Service - Self-Healing MT5 Connection Monitor
Monitors MT5 terminal health and automatically recovers from failures.
"""

import MetaTrader5 as mt5
import subprocess
import time
import psutil
import logging
import threading
from pathlib import Path

logger = logging.getLogger(__name__)

class MT5Watchdog:
    """
    Monitors MT5 terminal health and provides auto-recovery.
    """
    
    def __init__(self, mt5_path, login, password, server, check_interval=10):
        self.mt5_path = mt5_path
        self.login = int(login)
        self.password = password
        self.server = server
        self.check_interval = check_interval
        self.running = False
        self._thread = None
        
    def is_mt5_running(self):
        """Check if MT5 terminal process is active."""
        for proc in psutil.process_iter(attrs=["name"]):
            try:
                if proc.info["name"].lower() == "terminal64.exe":
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
    
    def start_mt5_terminal(self):
        """Launch MT5 terminal if not running."""
        if not Path(self.mt5_path).exists():
            logger.error(f"MT5 executable not found at {self.mt5_path}")
            return False
            
        logger.info("Starting MT5 terminal...")
        subprocess.Popen(
            [self.mt5_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=False
        )
        time.sleep(10)  # Wait for terminal to initialize
        return True
    
    def check_ipc_health(self):
        """Verify MT5 IPC connection is alive."""
        try:
            account = mt5.account_info()
            terminal = mt5.terminal_info()
            
            if account is None:
                return False, "No account info"
            
            if terminal and not terminal.connected:
                return False, "Terminal not connected to broker"
                
            return True, "OK"
        except Exception as e:
            return False, str(e)
    
    def check_ea_heartbeat(self, robot_id, max_age=60):
        """Check if EA is sending heartbeat signals."""
        try:
            gv_name = f"EA_HEARTBEAT_{robot_id}"
            if not mt5.global_variable_check(gv_name):
                return False, "Heartbeat variable not found"
            
            last_beat = mt5.global_variable_get(gv_name)
            age = time.time() - last_beat
            
            if age > max_age:
                return False, f"Heartbeat stale ({age:.0f}s old)"
                
            return True, "OK"
        except Exception as e:
            return False, str(e)
    
    def recover_connection(self):
        """Attempt to recover MT5 connection."""
        logger.warning("Attempting MT5 connection recovery...")
        
        # Step 1: Ensure terminal is running
        if not self.is_mt5_running():
            logger.info("MT5 not running, starting terminal...")
            if not self.start_mt5_terminal():
                return False
        
        # Step 2: Reinitialize IPC
        try:
            mt5.shutdown()
            time.sleep(2)
            
            success = mt5.initialize(
                login=self.login,
                password=self.password,
                server=self.server,
                timeout=20000
            )
            
            if not success:
                err_code, err_msg = mt5.last_error()
                logger.error(f"MT5 reinitialization failed: {err_code} - {err_msg}")
                return False
            
            # Verify account
            account = mt5.account_info()
            if account is None:
                logger.error("MT5 connected but account not authorized")
                return False
                
            logger.info(f"MT5 connection recovered successfully. Account: {account.login}")
            return True
            
        except Exception as e:
            logger.exception(f"Recovery failed: {e}")
            return False
    
    def _watchdog_loop(self, robot_id=None):
        """Main watchdog monitoring loop."""
        logger.info("MT5 Watchdog started")
        consecutive_failures = 0
        
        while self.running:
            try:
                # Check 1: Terminal process
                if not self.is_mt5_running():
                    logger.warning("MT5 terminal not running")
                    if self.recover_connection():
                        consecutive_failures = 0
                    else:
                        consecutive_failures += 1
                
                # Check 2: IPC health
                else:
                    ipc_ok, ipc_msg = self.check_ipc_health()
                    if not ipc_ok:
                        logger.warning(f"MT5 IPC unhealthy: {ipc_msg}")
                        if self.recover_connection():
                            consecutive_failures = 0
                        else:
                            consecutive_failures += 1
                    else:
                        consecutive_failures = 0
                
                # Check 3: EA heartbeat (if robot_id provided)
                if robot_id and consecutive_failures == 0:
                    hb_ok, hb_msg = self.check_ea_heartbeat(robot_id)
                    if not hb_ok:
                        logger.warning(f"EA heartbeat issue for robot {robot_id}: {hb_msg}")
                
                # Alert if too many consecutive failures
                if consecutive_failures >= 3:
                    logger.critical(f"MT5 Watchdog: {consecutive_failures} consecutive recovery failures!")
                
            except Exception as e:
                logger.exception(f"Watchdog loop error: {e}")
            
            time.sleep(self.check_interval)
        
        logger.info("MT5 Watchdog stopped")
    
    def start(self, robot_id=None):
        """Start the watchdog in a background thread."""
        if self.running:
            logger.warning("Watchdog already running")
            return
        
        self.running = True
        self._thread = threading.Thread(
            target=self._watchdog_loop,
            args=(robot_id,),
            daemon=True,
            name="MT5Watchdog"
        )
        self._thread.start()
        logger.info("MT5 Watchdog thread started")
    
    def stop(self):
        """Stop the watchdog."""
        self.running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("MT5 Watchdog stopped")
