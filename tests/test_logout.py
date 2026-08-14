from app.auth import keychain

def test_keychain_delete_handles_missing_token(monkeypatch):
    def missing(*args): raise keychain.keyring.errors.PasswordDeleteError("missing")
    monkeypatch.setattr(keychain.keyring,"delete_password",missing)
    keychain.delete_token()

def test_gui_has_no_dry_run_branch():
    from pathlib import Path
    source=(Path(__file__).parents[1]/"app/gui/main_window.py").read_text(encoding="utf-8")
    assert "self.dry" not in source
    assert "DRY RUN" not in source
