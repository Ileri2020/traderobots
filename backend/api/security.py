from cryptography.fernet import Fernet
from django.conf import settings
import os

# Use settings if configured, otherwise env directly for standalone scripts
try:
    key = settings.MT5_CREDENTIAL_SECRET
except:
    from dotenv import load_dotenv
    load_dotenv()
    key = os.getenv("MT5_CREDENTIAL_SECRET")

if not key:
    raise ValueError("MT5_CREDENTIAL_SECRET not set in environment or settings")

cipher = Fernet(key)

def encrypt(value: str) -> bytes:
    """Encrypts a string value into bytes."""
    if not value: return b""
    return cipher.encrypt(value.encode())

def decrypt(value: bytes) -> str:
    """Decrypts bytes back into a string."""
    if not value: return ""
    try:
        # If it's stored as bytes in DB (BinaryField), it comes out as bytes
        # If passed as string representation of bytes, handling might be needed but BinaryField should be bytes.
        if isinstance(value, memoryview):
            value = bytes(value)
        return cipher.decrypt(value).decode()
    except Exception as e:
        # Fallback or re-raise depending on strictness
        raise ValueError(f"Decryption failed: {e}")
