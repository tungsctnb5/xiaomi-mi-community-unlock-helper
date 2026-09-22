from types import SimpleNamespace

import pytest

from app.auth import keychain


@pytest.fixture(autouse=True)
def isolated_store(monkeypatch):
    values = {}
    def remove(service, account):
        values.pop((service, account), None)
    backend = SimpleNamespace(
        get_password=lambda service, account: values.get((service, account)),
        set_password=lambda service, account, token: values.__setitem__((service, account), token),
        delete_password=remove,
    )
    monkeypatch.setattr(keychain, "_backend", lambda: backend)
    monkeypatch.setattr(keychain, "_storage_error", None)
    return backend


def test_store_roundtrip_and_logout():
    assert keychain.load_token() is None
    assert keychain.save_token("  fake-token-for-tests  ")
    assert keychain.load_token() == "fake-token-for-tests"
    assert keychain.delete_token()
    assert keychain.load_token() is None


@pytest.mark.parametrize("error", [keychain.keyring.errors.NoKeyringError,
                                    keychain.keyring.errors.KeyringLocked, RuntimeError])
def test_missing_or_locked_store_does_not_abort_session(monkeypatch, error):
    def unavailable():
        raise error("fake-token-that-must-not-leak")
    monkeypatch.setattr(keychain, "_backend", unavailable)
    assert keychain.load_token() is None
    assert not keychain.save_token("fake-token-that-must-not-leak")
    assert not keychain.delete_token()
    assert "fake-token" not in keychain.storage_error()


def test_failed_save_is_not_reported_as_persisted(isolated_store):
    def denied(*args):
        raise PermissionError("denied")
    isolated_store.set_password = denied
    assert not keychain.save_token("fake-session")
    assert "could not be saved" in keychain.storage_error()
    assert keychain.load_token() is None


def test_failed_delete_leaves_explicit_retry_message(isolated_store):
    assert keychain.save_token("fake-session")
    def denied(*args):
        raise PermissionError("denied")
    isolated_store.delete_password = denied
    assert not keychain.delete_token()
    assert "retry Logout" in keychain.storage_error()


def test_recovered_backend_clears_warning(monkeypatch, isolated_store):
    def denied(*args):
        raise RuntimeError("offline")
    monkeypatch.setattr(isolated_store, "get_password", denied)
    assert keychain.load_token() is None
    assert keychain.storage_error()
    assert keychain.save_token("fake-session")
    assert keychain.storage_error() is None


def test_gui_keeps_current_token_when_secure_save_fails(monkeypatch):
    from unittest.mock import Mock
    from app.gui import main_window as gui
    monkeypatch.setattr(gui, "save_token", lambda token: False)
    monkeypatch.setattr(gui, "storage_error", lambda: "Secure store unavailable")
    monkeypatch.setattr(gui.QTimer, "singleShot", Mock())
    window = SimpleNamespace(token="", _set_session=Mock(), _log=Mock(), check_session=Mock(),
                             network_label=Mock())
    gui.MainWindow._browser_token(window, "fake-memory-only-token")
    assert window.token == "fake-memory-only-token"
    window._log.assert_any_call("Secure store unavailable")
    gui.QTimer.singleShot.assert_called_once_with(100, window.check_session)


def test_gui_logout_clears_active_session_even_if_store_is_locked(monkeypatch):
    from unittest.mock import Mock
    from app.gui import main_window as gui
    monkeypatch.setattr(gui, "delete_token", lambda: False)
    monkeypatch.setattr(gui, "storage_error", lambda: "Unlock keyring and retry Logout")
    monkeypatch.setattr(gui, "clear_browser_session", Mock(return_value=None))
    window = SimpleNamespace(network_cancel=Mock(), prepare_cancel=Mock(), scheduler=Mock(), dispatcher=None,
                             _stop_caffeinate=Mock(), login_window=None, token="fake-session",
                             client=object(), channels=[object()], _set_session=Mock(),
                             start_btn=Mock(), cancel_btn=Mock(), network_label=Mock(), _log=Mock())
    gui.MainWindow.logout(window)
    assert not window.token and window.client is None and window.channels == []
    window._log.assert_called_once_with("Unlock keyring and retry Logout")
