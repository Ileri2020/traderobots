import MetaTrader5 as mt5
from pathlib import Path
from api.security import decrypt
import os
from django.conf import settings

# Use the user-provided path or a fallback if permission issues arise
# Using a local directory within the project or user profile is often safer
# But adhering to the prompt:
BASE_DIR = Path("C:/mt5_users")

class UserMT5Manager:
    def __init__(self, user_id, account):
        self.user_id = user_id
        self.account = account
        self.user_dir = BASE_DIR / f"user_{user_id}"

    def connect(self):
        self.user_dir.mkdir(parents=True, exist_ok=True)

        # Get the global path from settings or env
        mt5_path = getattr(settings, 'MT5_PATH', os.getenv('MT5_PATH'))
        
        if not mt5_path:
            # Fallback or error
            raise Exception("MT5_PATH not configured in settings or env")

        if not mt5.initialize(
            path=mt5_path,
            data_path=str(self.user_dir)
        ):
            raise Exception(f"MT5 init failed: {mt5.last_error()}")

        if not self.account.mt5_login:
            raise Exception("Account login ID is missing.")

        authorized = mt5.login(
            int(self.account.mt5_login),
            decrypt(self.account.mt5_password),
            self.account.mt5_server
        )

        if not authorized:
            err = mt5.last_error()
            mt5.shutdown()
            raise Exception(f"MT5 login failed: {err}")

    def shutdown(self):
        mt5.shutdown()
