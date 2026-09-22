"""Shown-window regressions; CI also runs these on native Windows at four scales."""

import json
import os
from pathlib import Path

import pytest
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QStyleFactory

from app.gui.main_window import MainWindow


@pytest.fixture(scope="module")
def app():
    instance = QApplication.instance() or QApplication([])
    return instance


@pytest.fixture
def window(app, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Layout tests must not access credentials or start network requests")

    monkeypatch.setattr("app.gui.main_window.load_token", forbidden)
    monkeypatch.setattr("app.gui.main_window.stable_device_id", forbidden)
    monkeypatch.setattr(MainWindow, "_sync_ntp", forbidden)
    result = MainWindow(smoke_test=True)
    yield result
    result.close()
    result.deleteLater()
    app.processEvents()


def settle(app):
    for _ in range(4):
        app.processEvents()
    QTest.qWait(30)


def save_screenshot(window, name):
    if folder := os.environ.get("XIAOMI_LAYOUT_ARTIFACTS"):
        target = Path(folder)
        target.mkdir(parents=True, exist_ok=True)
        assert window.grab().save(str(target / f"{name}.png"))
        (target / f"{name}.json").write_text(
            json.dumps(layout_diagnostics(window), indent=2), encoding="utf-8")


def layout_diagnostics(window):
    from PySide6.QtWidgets import QWidget
    widgets = [window.scroll.widget(), *window.scroll.widget().findChildren(QWidget)]
    return {
        "window": window.size().toTuple(),
        "viewport": window.scroll.viewport().size().toTuple(),
        "screen": window.screen().availableGeometry().getRect(),
        "device_pixel_ratio": window.devicePixelRatioF(),
        "platform": QApplication.platformName(),
        "style": QApplication.style().objectName(),
        "widgets": [(type(widget).__name__, widget.objectName(), widget.size().toTuple(),
                     widget.minimumSize().toTuple(), widget.minimumSizeHint().toTuple())
                    for widget in widgets if widget.minimumSizeHint().width() > 250],
    }


@pytest.mark.parametrize("size", [(980, 820), (880, 720), (640, 460), (1200, 900)])
def test_automatic_execution_controls_fit_at_window_sizes(app, window, size):
    window.show()
    settle(app)
    window.resize(*size)
    settle(app)
    window.scroll.ensureWidgetVisible(window.start_btn)
    settle(app)
    assert not hasattr(window, "offset_spins")
    assert not hasattr(window, "attempt_fields")
    assert not hasattr(window, "adaptive")
    for control in (window.measure_btn, window.start_btn, window.cancel_btn):
        assert control.height() >= control.sizeHint().height()
        assert control.width() >= control.sizeHint().width()
    assert window.scroll.horizontalScrollBar().maximum() == 0, layout_diagnostics(window)
    if window.height() <= 460:
        assert window.scroll.verticalScrollBar().maximum() > 0
    save_screenshot(window, f"window-{size[0]}x{size[1]}")


def test_automatic_controls_remain_readable_across_qt_styles(app, window):
    original = app.style().objectName()
    window.show()
    settle(app)
    try:
        for style in QStyleFactory.keys():
            app.setStyle(style)
            window.resize(880, 720)
            settle(app)
            for control in (window.measure_btn, window.start_btn, window.cancel_btn):
                assert control.width() >= control.sizeHint().width()
            assert window.scroll.horizontalScrollBar().maximum() == 0
    finally:
        app.setStyle(original)


def test_no_manual_timing_controls_return_after_resize(app, window):
    window.show()
    settle(app)
    for size in ((1200, 900), (640, 460), (980, 820)):
        window.resize(*size)
        settle(app)
        assert not hasattr(window, "offset_spins")
        assert not hasattr(window, "attempt_fields")
        assert not hasattr(window, "adaptive")
        assert window.scroll.horizontalScrollBar().maximum() == 0, (size, layout_diagnostics(window))
