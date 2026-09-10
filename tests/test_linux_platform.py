from types import SimpleNamespace
import threading
from unittest.mock import Mock

import pytest

from app import platform_support as platform


@pytest.fixture
def linux(monkeypatch):
    monkeypatch.setattr(platform.sys, "platform", "linux")


@pytest.fixture
def helper(monkeypatch, linux):
    process = Mock()
    process.pid = 12345
    process.poll.return_value = None
    process.wait.return_value = 0
    process.stdout.fileno.return_value = 91
    monkeypatch.setattr(platform.shutil, "which", lambda name: "/usr/bin/systemd-inhibit")
    spawn = Mock(return_value=process)
    monkeypatch.setattr(platform.subprocess, "Popen", spawn)
    monkeypatch.setattr(platform.select, "select", lambda *args: ([process.stdout], [], []))
    monkeypatch.setattr(platform.os, "read", lambda *args: platform.SleepInhibitor._READY)
    kill_group = Mock()
    monkeypatch.setattr(platform.os, "killpg", kill_group, raising=False)
    monkeypatch.setattr(platform.signal, "SIGKILL", 9, raising=False)
    return SimpleNamespace(process=process, spawn=spawn, kill_group=kill_group)


def test_linux_xdg_data_home(monkeypatch, linux, tmp_path):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    assert platform.app_data_dir() == tmp_path / platform.APP_NAME


def test_linux_xdg_default(monkeypatch, linux, tmp_path):
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    monkeypatch.setattr(platform.Path, "home", lambda: tmp_path)
    assert platform.app_data_dir() == tmp_path / ".local" / "share" / platform.APP_NAME


def test_linux_inhibition_acquired_only_after_handshake(helper):
    inhibitor = platform.SleepInhibitor()
    assert inhibitor.start() is True
    assert inhibitor.active
    args, kwargs = helper.spawn.call_args
    assert "--what=idle:sleep" in args[0]
    assert "--mode=block" in args[0]
    assert "--no-ask-password" in args[0]
    assert kwargs["start_new_session"] is True
    assert inhibitor.start() is True
    assert helper.spawn.call_count == 1
    inhibitor.stop()
    assert not inhibitor.active
    assert inhibitor.process is None
    helper.process.stdin.close.assert_called_once()
    helper.process.stdout.close.assert_called_once()
    helper.kill_group.assert_not_called()
    inhibitor.stop()
    helper.process.stdin.close.assert_called_once()


def test_linux_partial_readiness_record(monkeypatch, helper):
    chunks = iter([b"XIAOMI_", b"INHIBIT_READY\n"])
    monkeypatch.setattr(platform.os, "read", lambda *args: next(chunks))
    inhibitor = platform.SleepInhibitor()
    assert inhibitor.start() is True
    inhibitor.stop()


def test_linux_missing_inhibit_command(monkeypatch, linux):
    monkeypatch.setattr(platform.shutil, "which", lambda name: None)
    spawn = Mock()
    monkeypatch.setattr(platform.subprocess, "Popen", spawn)
    inhibitor = platform.SleepInhibitor()
    assert inhibitor.start() is False
    assert not inhibitor.active
    assert "unavailable" in inhibitor.reason
    spawn.assert_not_called()


@pytest.mark.parametrize("failure", ["timeout", "eof", "malformed", "exited", "spawn"])
def test_linux_acquisition_failures_do_not_report_success(monkeypatch, helper, failure):
    if failure == "timeout":
        monkeypatch.setattr(platform.select, "select", lambda *args: ([], [], []))
    elif failure == "eof":
        monkeypatch.setattr(platform.os, "read", lambda *args: b"")
    elif failure == "malformed":
        monkeypatch.setattr(platform.os, "read", lambda *args: b"x" * len(platform.SleepInhibitor._READY))
    elif failure == "exited":
        helper.process.poll.return_value = 1
    else:
        helper.spawn.side_effect = OSError("unavailable")
    inhibitor = platform.SleepInhibitor()
    assert inhibitor.start() is False
    assert not inhibitor.active
    assert inhibitor.process is None
    assert inhibitor.reason
    if failure != "spawn":
        helper.process.stdin.close.assert_called_once()
        helper.process.stdout.close.assert_called_once()


def test_linux_stalled_helper_is_terminated_as_owned_process_group(monkeypatch, helper):
    monkeypatch.setattr(platform.select, "select", lambda *args: ([], [], []))
    helper.process.wait.side_effect = [
        platform.subprocess.TimeoutExpired("inhibit", 0.3),
        platform.subprocess.TimeoutExpired("inhibit", 0.5),
        0,
    ]
    inhibitor = platform.SleepInhibitor()
    assert inhibitor.start() is False
    assert [call.args for call in helper.kill_group.call_args_list] == [
        (12345, platform.signal.SIGTERM), (12345, platform.signal.SIGKILL),
    ]


def test_windows_api_failure_does_not_report_success(monkeypatch):
    import ctypes
    monkeypatch.setattr(platform.sys, "platform", "win32")
    execution_state = Mock(return_value=0)
    monkeypatch.setattr(ctypes, "windll", SimpleNamespace(
        kernel32=SimpleNamespace(SetThreadExecutionState=execution_state)
    ), raising=False)
    inhibitor = platform.SleepInhibitor()
    assert inhibitor.start() is False
    assert not inhibitor.active


def test_macos_start_reports_process_launch_failure(monkeypatch):
    monkeypatch.setattr(platform.sys, "platform", "darwin")
    monkeypatch.setattr(platform.subprocess, "Popen", Mock(side_effect=OSError("missing")))
    inhibitor = platform.SleepInhibitor()
    assert inhibitor.start() is False
    assert not inhibitor.active


class ControlledInhibitor:
    """Fake OS calls controlled by events; never inhibits the real machine."""
    def __init__(self, *, result=True):
        self.started = threading.Event()
        self.finish_start = threading.Event()
        self.stopping = threading.Event()
        self.finish_stop = threading.Event()
        self.finish_stop.set()
        self.stopped = threading.Event()
        self.result = result
        self.reason = "Mock inhibition unavailable"
        self.stop_calls = 0

    def start(self):
        self.started.set()
        if not self.finish_start.wait(2):
            raise TimeoutError("Test did not release mocked acquisition")
        return self.result

    def stop(self):
        self.stop_calls += 1
        self.stopping.set()
        if not self.finish_stop.wait(2):
            raise TimeoutError("Test did not release mocked cleanup")
        self.stopped.set()


def test_async_cancel_during_pending_acquisition_releases_late_lock():
    underlying = ControlledInhibitor()
    wrapper = platform.AsyncSleepInhibitor(inhibitor_factory=lambda: underlying)
    messages = []
    wrapper.start(messages.append)
    try:
        assert underlying.started.wait(1)
        wrapper.stop()
        assert not wrapper.active
        assert not underlying.stopping.is_set()
        underlying.finish_start.set()
        assert underlying.stopped.wait(1)
        assert messages == []
        assert underlying.stop_calls == 1
    finally:
        underlying.finish_start.set()
        wrapper.stop()


def test_async_rapid_restart_releases_stale_acquisition_only_once():
    old, new = ControlledInhibitor(), ControlledInhibitor()
    candidates = iter((old, new))
    wrapper = platform.AsyncSleepInhibitor(inhibitor_factory=lambda: next(candidates))
    delivered = threading.Event()
    messages = []
    wrapper.start(lambda text: messages.append(("old", text)))
    try:
        assert old.started.wait(1)
        wrapper.start(lambda text: (messages.append(("new", text)), delivered.set()))
        assert new.started.wait(1)
        old.finish_start.set()
        assert old.stopped.wait(1)
        assert not wrapper.active
        new.finish_start.set()
        assert delivered.wait(1)
        assert wrapper.active
        assert messages == [("new", "Sleep prevention enabled")]
        wrapper.stop()
        assert new.stopped.wait(1)
        assert old.stop_calls == new.stop_calls == 1
    finally:
        old.finish_start.set()
        new.finish_start.set()
        wrapper.stop()


def test_async_slow_cleanup_does_not_block_stop_or_new_acquisition():
    old, new = ControlledInhibitor(), ControlledInhibitor()
    old.finish_start.set()
    old.finish_stop.clear()
    new.finish_start.set()
    candidates = iter((old, new))
    wrapper = platform.AsyncSleepInhibitor(inhibitor_factory=lambda: next(candidates))
    old_ready, new_ready = threading.Event(), threading.Event()
    wrapper.start(lambda text: old_ready.set())
    try:
        assert old_ready.wait(1)
        wrapper.stop()
        assert old.stopping.wait(1)
        assert not old.stopped.is_set()
        wrapper.start(lambda text: new_ready.set())
        assert new_ready.wait(1)
        assert wrapper.active
        assert not old.stopped.is_set()
        old.finish_stop.set()
        assert old.stopped.wait(1)
        assert wrapper.active
        wrapper.stop()
        assert new.stopped.wait(1)
    finally:
        old.finish_stop.set()
        wrapper.stop()


def test_async_failure_reports_status_without_active_lock():
    underlying = ControlledInhibitor(result=False)
    underlying.finish_start.set()
    wrapper = platform.AsyncSleepInhibitor(inhibitor_factory=lambda: underlying)
    delivered = threading.Event()
    messages = []
    wrapper.start(lambda text: (messages.append(text), delivered.set()))
    assert delivered.wait(1)
    assert not wrapper.active
    assert underlying.stopped.is_set()
    assert messages == ["Mock inhibition unavailable"]


def test_async_closed_gui_callback_releases_owned_lock():
    underlying = ControlledInhibitor()
    underlying.finish_start.set()
    wrapper = platform.AsyncSleepInhibitor(inhibitor_factory=lambda: underlying)

    def closed_gui(text):
        raise RuntimeError("GUI has closed")

    wrapper.start(closed_gui)
    assert underlying.stopped.wait(1)
    assert not wrapper.active
    assert underlying.stop_calls == 1
