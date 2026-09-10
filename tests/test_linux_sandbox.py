import subprocess
from types import SimpleNamespace

import pytest

from app.auth import linux_sandbox


@pytest.mark.parametrize("returncode,expected", [(0, True), (1, False)])
def test_linux_namespace_check_is_isolated(monkeypatch, returncode, expected):
    monkeypatch.setattr(linux_sandbox.sys, "platform", "linux")
    monkeypatch.setattr(linux_sandbox.os, "geteuid", lambda: 1000, raising=False)
    commands = []
    def run(command, **kwargs):
        commands.append((command, kwargs))
        return SimpleNamespace(returncode=returncode)
    monkeypatch.setattr(linux_sandbox.subprocess, "run", run)
    assert linux_sandbox.browser_sandbox_available() is expected
    assert commands[0][0][-1] == "--check-browser-sandbox"
    assert commands[0][1]["timeout"] == 5


def test_linux_root_does_not_launch_renderer(monkeypatch):
    monkeypatch.setattr(linux_sandbox.sys, "platform", "linux")
    monkeypatch.setattr(linux_sandbox.os, "geteuid", lambda: 0, raising=False)
    def forbidden(*args, **kwargs):
        pytest.fail("Root must be rejected before spawning a process")
    monkeypatch.setattr(linux_sandbox.subprocess, "run", forbidden)
    assert not linux_sandbox.browser_sandbox_available()


def test_probe_timeout_is_safe_failure(monkeypatch):
    monkeypatch.setattr(linux_sandbox.sys, "platform", "linux")
    monkeypatch.setattr(linux_sandbox.os, "geteuid", lambda: 1000, raising=False)
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired("probe", 5)
    monkeypatch.setattr(linux_sandbox.subprocess, "run", timeout)
    assert not linux_sandbox.browser_sandbox_available()
