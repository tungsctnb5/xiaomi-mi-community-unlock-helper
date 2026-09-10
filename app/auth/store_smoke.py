"""Synthetic Secret Service integration check for an isolated CI D-Bus session."""

import sys
import uuid


def run() -> int:
    if not sys.platform.startswith("linux"):
        return 1
    from keyring.backends.SecretService import Keyring

    store = Keyring()
    service = "xiaomi-helper-build-check-" + uuid.uuid4().hex
    account = "synthetic-ci-account"
    token = "synthetic-ci-value"
    saved = False
    try:
        store.set_password(service, account, token)
        saved = True
        if store.get_password(service, account) != token:
            return 1
        store.delete_password(service, account)
        saved = False
        return 0 if store.get_password(service, account) is None else 1
    except Exception:
        return 1
    finally:
        if saved:
            try:
                store.delete_password(service, account)
            except Exception:
                pass
