import keyring

SERVICE = "com.local.XiaomiUnlockHelper"
ACCOUNT = "new_bbs_serviceToken"

def save_token(token: str) -> None:
    keyring.set_password(SERVICE, ACCOUNT, token.strip())

def load_token() -> str | None:
    return keyring.get_password(SERVICE, ACCOUNT)

def delete_token() -> None:
    try:
        keyring.delete_password(SERVICE, ACCOUNT)
    except keyring.errors.PasswordDeleteError:
        pass
