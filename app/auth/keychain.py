import sys

import keyring

SERVICE = "com.local.XiaomiUnlockHelper"
ACCOUNT = "new_bbs_serviceToken"
_storage_error = None


def storage_error() -> str | None:
    return _storage_error


def _backend():
    if sys.platform.startswith("linux"):
        # Only use an encrypted desktop store, never a plaintext keyrings.alt backend.
        from keyring.backends.SecretService import Keyring
        return Keyring()
    return keyring


def save_token(token: str) -> bool:
    global _storage_error
    try:
        _backend().set_password(SERVICE, ACCOUNT, token.strip())
        _storage_error = None
        return True
    except Exception:
        # Backend exceptions can include supplied values; do not surface raw errors.
        _storage_error = "Secure credential store unavailable. Current session remains usable; the token could not be saved."
        return False


def load_token() -> str | None:
    global _storage_error
    try:
        token = _backend().get_password(SERVICE, ACCOUNT)
        _storage_error = None
        return token
    except Exception:
        _storage_error = "Secure credential store unavailable. Login or paste a token to use this session."
        return None


def delete_token() -> bool:
    global _storage_error
    try:
        _backend().delete_password(SERVICE, ACCOUNT)
    except keyring.errors.PasswordDeleteError:
        _storage_error = None
        return True
    except Exception:
        _storage_error = "Could not delete the saved session. Unlock your system keyring and retry Logout."
        return False
    _storage_error = None
    return True
