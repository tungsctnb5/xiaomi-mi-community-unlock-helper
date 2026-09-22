import time
from types import SimpleNamespace

import pytest
from PySide6.QtWidgets import QApplication

from app.gui.main_window import MainWindow


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def window(app):
    result = MainWindow(smoke_test=True)
    result.token = "fake-test-token"
    result.client = SimpleNamespace(token="fake-test-token")
    yield result
    result.close()
    result.deleteLater()
    app.processEvents()


def test_start_without_profile_automatically_measures(window, monkeypatch):
    calls = []
    monkeypatch.setattr(window, "measure_network", lambda *, start_after=False: calls.append(start_after))

    window.start()

    assert calls == [True]


def test_begin_start_uses_measured_profile_without_manual_fields(window, monkeypatch):
    profile = SimpleNamespace(arrival_offsets_ms=(-110, 30, 150, 340))
    window.network_profile = profile
    window.network_measured_at = time.monotonic()
    captured = {}

    class FakeThread:
        def __init__(self, *, target, args, daemon):
            captured.update(target=target, args=args, daemon=daemon)
        def start(self):
            captured["started"] = True

    monkeypatch.setattr("app.gui.main_window.threading.Thread", FakeThread)
    monkeypatch.setattr(window, "_start_caffeinate", lambda: None)

    window._begin_start()

    assert captured["args"][1] == [-110, 30, 150, 340]
    assert captured["args"][2] == "LIVE"
    assert captured["daemon"] is True
    assert captured["started"] is True
    assert not hasattr(window, "offset_spins")
    assert not hasattr(window, "adaptive")
