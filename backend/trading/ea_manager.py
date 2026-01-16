"""
EA Manager - Handles Expert Advisor deployment and confirmation
Ensures EAs are properly loaded, running, and communicating.
"""

import MetaTrader5 as mt5
import time
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class EAManager:
    """
    Manages EA deployment, injection confirmation, and heartbeat monitoring.
    """
    
    @staticmethod
    def wait_for_ea_ready(robot_id, timeout=30):
        """
        Wait for EA to signal it's ready via global variable.
        
        Args:
            robot_id: Unique robot identifier
            timeout: Maximum seconds to wait
            
        Returns:
            bool: True if EA ready signal detected
            
        Raises:
            RuntimeError: If EA doesn't signal ready within timeout
        """
        gv_ready = f"EA_READY_{robot_id}"
        start = time.time()
        
        logger.info(f"Waiting for EA ready signal: {gv_ready}")
        
        while time.time() - start < timeout:
            if mt5.global_variable_check(gv_ready):
                ready_time = mt5.global_variable_get(gv_ready)
                logger.info(f"EA {robot_id} ready signal detected at {ready_time}")
                return True
            time.sleep(1)
        
        raise RuntimeError(
            f"EA injection failed: EA_READY_{robot_id} not found after {timeout}s. "
            "EA may not be loaded or OnInit() failed."
        )
    
    @staticmethod
    def wait_for_ea_heartbeat(robot_id, timeout=30):
        """
        Wait for EA heartbeat file to appear.
        
        Args:
            robot_id: Unique robot identifier
            timeout: Maximum seconds to wait
            
        Returns:
            bool: True if heartbeat file detected
            
        Raises:
            RuntimeError: If heartbeat file doesn't appear within timeout
        """
        try:
            terminal_info = mt5.terminal_info()
            if not terminal_info:
                raise RuntimeError("Cannot get terminal info - MT5 not initialized")
            
            data_path = terminal_info.data_path
            heartbeat_file = Path(data_path) / "MQL5" / "Files" / f"heartbeat_{robot_id}.txt"
            
            logger.info(f"Waiting for EA heartbeat file: {heartbeat_file}")
            
            start = time.time()
            while time.time() - start < timeout:
                if heartbeat_file.exists():
                    # Read the heartbeat to verify it's valid
                    try:
                        with open(heartbeat_file, 'r') as f:
                            content = f.read().strip()
                        logger.info(f"EA {robot_id} heartbeat detected: {content}")
                        return True
                    except Exception as e:
                        logger.warning(f"Heartbeat file exists but couldn't read: {e}")
                
                time.sleep(1)
            
            raise RuntimeError(
                f"EA heartbeat not detected after {timeout}s. "
                f"Expected file: {heartbeat_file}"
            )
            
        except Exception as e:
            raise RuntimeError(f"Heartbeat check failed: {e}")
    
    @staticmethod
    def check_ea_alive(robot_id, max_age=60):
        """
        Check if EA is currently alive and sending heartbeats.
        
        Args:
            robot_id: Unique robot identifier
            max_age: Maximum acceptable age of heartbeat in seconds
            
        Returns:
            tuple: (is_alive: bool, message: str)
        """
        try:
            # Check global variable heartbeat
            gv_heartbeat = f"EA_HEARTBEAT_{robot_id}"
            
            if not mt5.global_variable_check(gv_heartbeat):
                return False, "Heartbeat global variable not found"
            
            last_beat = mt5.global_variable_get(gv_heartbeat)
            current_time = time.time()
            age = current_time - last_beat
            
            if age > max_age:
                return False, f"Heartbeat stale: {age:.0f}s old (max {max_age}s)"
            
            return True, f"Alive (heartbeat {age:.0f}s ago)"
            
        except Exception as e:
            return False, f"Error checking heartbeat: {e}"
    
    @staticmethod
    def get_ea_status(robot_id):
        """
        Get comprehensive EA status information.
        
        Args:
            robot_id: Unique robot identifier
            
        Returns:
            dict: Status information including ready state, heartbeat, etc.
        """
        status = {
            "robot_id": robot_id,
            "ready": False,
            "heartbeat_active": False,
            "heartbeat_age": None,
            "errors": []
        }
        
        try:
            # Check ready signal
            gv_ready = f"EA_READY_{robot_id}"
            if mt5.global_variable_check(gv_ready):
                status["ready"] = True
            else:
                status["errors"].append("EA_READY signal not found")
            
            # Check heartbeat
            is_alive, msg = EAManager.check_ea_alive(robot_id)
            status["heartbeat_active"] = is_alive
            
            if is_alive:
                gv_heartbeat = f"EA_HEARTBEAT_{robot_id}"
                last_beat = mt5.global_variable_get(gv_heartbeat)
                status["heartbeat_age"] = time.time() - last_beat
            else:
                status["errors"].append(msg)
            
        except Exception as e:
            status["errors"].append(f"Status check error: {e}")
        
        return status
    
    @staticmethod
    def deploy_and_confirm(robot_id, symbol, timeframe, timeout=60):
        """
        Deploy EA and wait for full confirmation.
        
        This is the main deployment method that ensures the EA is:
        1. Loaded into MT5
        2. Initialized successfully
        3. Sending heartbeats
        
        Args:
            robot_id: Unique robot identifier
            symbol: Trading symbol
            timeframe: Chart timeframe
            timeout: Maximum time to wait for full confirmation
            
        Returns:
            dict: Deployment result with status and details
            
        Raises:
            RuntimeError: If deployment fails
        """
        result = {
            "robot_id": robot_id,
            "symbol": symbol,
            "timeframe": timeframe,
            "ready_confirmed": False,
            "heartbeat_confirmed": False,
            "chart_opened": False,
            "status": "PENDING"
        }
        
        try:
            # Step 1: Open chart (EA must be attached manually or via template)
            tf_map = {
                'M1': mt5.TIMEFRAME_M1, 'M5': mt5.TIMEFRAME_M5,
                'M15': mt5.TIMEFRAME_M15, 'H1': mt5.TIMEFRAME_H1,
                'H4': mt5.TIMEFRAME_H4, 'D1': mt5.TIMEFRAME_D1
            }
            mt5_tf = tf_map.get(timeframe, mt5.TIMEFRAME_H1)
            
            chart_id = mt5.chart_open(symbol, mt5_tf)
            if chart_id:
                result["chart_opened"] = True
                logger.info(f"Chart opened for {symbol} on {timeframe}")
            else:
                raise RuntimeError(f"Failed to open chart for {symbol}")
            
            # Step 2: Wait for EA ready signal
            try:
                EAManager.wait_for_ea_ready(robot_id, timeout=timeout//2)
                result["ready_confirmed"] = True
            except RuntimeError as e:
                logger.warning(f"EA ready signal timeout: {e}")
                # Continue to check heartbeat anyway
            
            # Step 3: Wait for heartbeat
            try:
                EAManager.wait_for_ea_heartbeat(robot_id, timeout=timeout//2)
                result["heartbeat_confirmed"] = True
            except RuntimeError as e:
                logger.warning(f"EA heartbeat timeout: {e}")
            
            # Determine final status
            if result["ready_confirmed"] and result["heartbeat_confirmed"]:
                result["status"] = "SUCCESS"
            elif result["heartbeat_confirmed"]:
                result["status"] = "PARTIAL"  # Heartbeat works but no ready signal
            else:
                result["status"] = "FAILED"
                raise RuntimeError(
                    "EA deployment failed: No confirmation signals received. "
                    "Ensure EA is compiled and attached to the chart."
                )
            
            return result
            
        except Exception as e:
            result["status"] = "FAILED"
            result["error"] = str(e)
            raise RuntimeError(f"EA deployment failed: {e}")
