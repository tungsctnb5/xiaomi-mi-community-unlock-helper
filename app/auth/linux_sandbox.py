"""Check Linux namespace support without changing the GUI process or system policy."""

import ctypes
import os
from pathlib import Path
import subprocess
import sys


def namespace_probe() -> int:
    if not sys.platform.startswith("linux"):
        return 0
    if os.geteuid() == 0:
        return 1
    try:
        libc = ctypes.CDLL(None, use_errno=True)
        # This is called only in a disposable subprocess, before QApplication.
        return 0 if libc.unshare(0x10000000) == 0 else 1  # CLONE_NEWUSER
    except (AttributeError, OSError):
        return 1


def browser_sandbox_available() -> bool:
    if not sys.platform.startswith("linux"):
        return True
    if os.geteuid() == 0:
        return False
    command = [sys.executable]
    if not getattr(sys, "frozen", False):
        command += ["-m", "app.main"]
    command.append("--check-browser-sandbox")
    try:
        result = subprocess.run(command, cwd=Path(__file__).parents[2],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                timeout=5, check=False)
        return result.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False
