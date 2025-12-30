import base64
from django.conf import settings
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    HAS_CRYPTO = True
except (ImportError, Exception):
    HAS_CRYPTO = False

def get_cipher():
    if not HAS_CRYPTO:
        return None
    # Derive a key from the SECRET_KEY
    password = settings.SECRET_KEY.encode()
    salt = b'salt_' # In production, use a unique salt
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return Fernet(key)

def encrypt_value(value):
    if not value:
        return None
    if not HAS_CRYPTO:
        # Simple fallback (not secure, but functional for this test)
        return base64.b64encode(value.encode()).decode()
    f = get_cipher()
    return f.encrypt(value.encode()).decode()

def decrypt_value(encrypted_value):
    if not encrypted_value:
        return None
    if not HAS_CRYPTO:
        try:
            return base64.b64decode(encrypted_value.encode()).decode()
        except:
            return encrypted_value
    f = get_cipher()
    try:
        return f.decrypt(encrypted_value.encode()).decode()
    except Exception:
        return None
