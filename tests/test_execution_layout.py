"""Shown-window regressions; CI also runs these on native Windows at four scales."""

import os
from pathlib import Path

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QStyle, QStyleFactory, QStyleOptionSpinBox

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


def assert_readable(spin):
    editor = spin.lineEdit()
    metrics = editor.fontMetrics()
    margins = editor.textMargins()
    rect = editor.contentsRect().marginsRemoved(margins)
    assert rect.height() >= metrics.height() + 2, (rect, metrics.height())
    assert rect.width() >= metrics.horizontalAdvance(spin.text()) + 4
    assert spin.rect().contains(editor.geometry())
    assert spin.parentWidget().rect().contains(spin.geometry())


@pytest.mark.parametrize("size", [(980, 820), (880, 720), (640, 460), (1200, 900)])
def test_attempt_text_and_controls_fit_at_window_sizes(app, window, size):
    window.resize(*size)
    window.show()
    settle(app)
    window.scroll.ensureWidgetVisible(window.attempt_fields)
    settle(app)
    try:
        for spin in window.offset_spins:
            for value in (-2000, -100, 0, 20, 120, 300, 5000):
                spin.setValue(value)
                assert_readable(spin)
        assert len({spin.width() for spin in window.offset_spins}) <= 2
        for first, second in zip(window.attempt_fields.fields, window.attempt_fields.fields[1:]):
            assert not first.geometry().intersects(second.geometry())
        for control in (window.adaptive, window.start_btn, window.cancel_btn):
            assert control.height() >= control.sizeHint().height()
            assert control.width() >= control.sizeHint().width()
        if size == (640, 460):
            assert window.attempt_fields.columns == 2
            assert window.scroll.verticalScrollBar().maximum() > 0
        if size == (1200, 900):
            assert window.attempt_fields.columns == 4
    finally:
        for spin, value in zip(window.offset_spins, (-100, 20, 120, 300)):
            spin.setValue(value)
        save_screenshot(window, f"window-{size[0]}x{size[1]}")


def test_fields_remain_readable_across_qt_styles(app, window):
    original = app.style().objectName()
    try:
        for style in QStyleFactory.keys():
            app.setStyle(style)
            window.resize(880, 720)
            window.show()
            settle(app)
            for spin in window.offset_spins:
                spin.setValue(-2000)
                assert_readable(spin)
    finally:
        app.setStyle(original)


def test_attempt_values_survive_resize_and_support_editing(app, window):
    window.show()
    settle(app)
    for size in ((1200, 900), (640, 460), (980, 820)):
        window.resize(*size)
        settle(app)
        assert [s.value() for s in window.offset_spins] == [-100, 20, 120, 300]
        assert window.attempt_fields.columns == (2 if size[0] == 640 else 4)
        assert window.scroll.horizontalScrollBar().maximum() == 0
        for spin in window.offset_spins:
            assert_readable(spin)

    for spin in window.offset_spins:
        window.scroll.ensureWidgetVisible(spin)
        spin.setFocus()
        spin.selectAll()
        QTest.keyClicks(spin, "-1234")
        QTest.keyClick(spin, Qt.Key_Return)
        assert spin.value() == -1234
        QTest.keyClick(spin, Qt.Key_Up)
        assert spin.value() == -1233
        option = QStyleOptionSpinBox()
        spin.initStyleOption(option)
        for subcontrol, value in ((QStyle.SC_SpinBoxUp, -1232), (QStyle.SC_SpinBoxDown, -1233)):
            button_rect = spin.style().subControlRect(QStyle.CC_SpinBox, option, subcontrol, spin)
            assert button_rect.width() >= 20 and button_rect.height() >= 15
            assert not button_rect.intersects(spin.lineEdit().geometry())
            QTest.mouseClick(spin, Qt.LeftButton, pos=button_rect.center())
            assert spin.value() == value
