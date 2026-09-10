import os
import select
import shutil
import signal
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

APP_NAME = "Xiaomi Mi Community Unlock Helper"

def app_data_dir() -> Path:
    if sys.platform == "win32":
        root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return root / APP_NAME
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Xiaomi Unlock Helper"
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / APP_NAME

class SleepInhibitor:
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001
    ES_DISPLAY_REQUIRED = 0x00000002
    ACQUIRE_TIMEOUT = 2.0
    _READY = b"XIAOMI_INHIBIT_READY\n"

    def __init__(self):
        self.process = None
        self.active = False
        self.reason = ""
        self._platform = sys.platform
        self._process_group = False

    def start(self) -> bool:
        if self.active:
            return True
        self.reason = ""
        self._platform = sys.platform
        try:
            if self._platform == "darwin":
                self.process = subprocess.Popen(["/usr/bin/caffeinate", "-dimsu"])
                if self.process.poll() is not None:
                    raise OSError("Sleep prevention process exited")
            elif self._platform == "win32":
                import ctypes
                result = ctypes.windll.kernel32.SetThreadExecutionState(
                    self.ES_CONTINUOUS | self.ES_SYSTEM_REQUIRED | self.ES_DISPLAY_REQUIRED
                )
                if not result:
                    raise OSError("Sleep prevention request failed")
            elif self._platform.startswith("linux"):
                return self._start_linux()
            else:
                self.reason = "Sleep prevention is unavailable on this operating system."
                return False
        except (OSError, AttributeError):
            self._release_process()
            self.reason = "System sleep prevention could not be enabled; keep the computer awake."
            return False
        self.active = True
        return True

    def _start_linux(self) -> bool:
        executable = shutil.which("systemd-inhibit")
        if not executable:
            self.reason = "systemd-inhibit is unavailable; disable automatic sleep while waiting."
            return False
        # systemd-inhibit starts its command only after acquiring the lock.
        # A READY record therefore acknowledges acquisition, not just process
        # launch. The shell waits on our stdin pipe; EOF releases the lock even
        # if this application crashes. No password, token or user input enters it.
        # https://systemd.io/INHIBITOR_LOCKS/
        command = [
            executable, "--what=idle:sleep", "--mode=block", "--no-ask-password",
            f"--who={APP_NAME}", "--why=Waiting for the scheduled Xiaomi application window",
            "/bin/sh", "-c", "printf 'XIAOMI_INHIBIT_READY\\n'; read -r _xiaomi_release",
        ]
        try:
            self.process = subprocess.Popen(
                command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL, bufsize=0, start_new_session=True,
            )
            self._process_group = True
            deadline = time.monotonic() + self.ACQUIRE_TIMEOUT
            received = b""
            while len(received) < len(self._READY):
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError
                readable, _, _ = select.select([self.process.stdout], [], [], remaining)
                if not readable:
                    raise TimeoutError
                chunk = os.read(self.process.stdout.fileno(), len(self._READY) - len(received))
                if not chunk:
                    raise OSError("Sleep prevention process exited")
                received += chunk
            if received != self._READY or self.process.poll() is not None:
                raise OSError("Sleep prevention was not acquired")
        except (OSError, ValueError):
            self._release_process()
            self.reason = "Linux sleep inhibition was denied or unavailable; disable automatic sleep while waiting."
            return False
        self.active = True
        return True

    def _release_process(self):
        process, self.process = self.process, None
        grouped, self._process_group = self._process_group, False
        if process is None:
            return
        # EOF normally lets the Linux helper exit immediately. The bounded
        # termination fallback also cleans up a helper stuck during acquisition.
        if process.stdin:
            try:
                process.stdin.close()
            except OSError:
                pass
        try:
            if process.poll() is None:
                if grouped:
                    try:
                        process.wait(timeout=0.3)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGTERM)
                else:
                    process.terminate()
                try:
                    process.wait(timeout=0.5)
                except subprocess.TimeoutExpired:
                    if grouped:
                        os.killpg(process.pid, signal.SIGKILL)
                    else:
                        process.kill()
                    process.wait(timeout=0.5)
        except (OSError, subprocess.TimeoutExpired):
            pass
        finally:
            if process.stdout:
                process.stdout.close()

    def stop(self):
        self._release_process()
        if self.active and self._platform == "win32":
            import ctypes
            ctypes.windll.kernel32.SetThreadExecutionState(self.ES_CONTINUOUS)
        self.active = False


@dataclass
class _AsyncInhibition:
    inhibitor: SleepInhibitor
    completed: bool = False
    acquired: bool = False


class AsyncSleepInhibitor:
    """Linux-only asynchronous ownership of a sleep inhibitor.

    Each start gets its own candidate. Pending candidates release themselves if
    cancellation or a newer start supersedes them. Callbacks run on a worker;
    GUI users must deliver their messages through a signal. A callback already
    being delivered when stop() runs may still arrive, so callbacks are status
    notifications only and must never arm the scheduler themselves.

    Windows must use SleepInhibitor directly: its API is thread-owned.
    """

    def __init__(self, *, inhibitor_factory=None):
        self._factory = inhibitor_factory or SleepInhibitor
        self._lock = threading.Lock()
        self._current = None

    @property
    def active(self) -> bool:
        with self._lock:
            return bool(self._current and self._current.acquired)

    def start(self, callback: Callable[[str], None]) -> None:
        candidate = _AsyncInhibition(self._factory())
        with self._lock:
            previous = self._current
            self._current = candidate
            release_previous = previous is not None and previous.completed
        if release_previous:
            self._release_later(previous)
        threading.Thread(target=self._acquire, args=(candidate, callback), daemon=True).start()

    def _acquire(self, candidate, callback):
        try:
            acquired = bool(candidate.inhibitor.start())
            message = "Sleep prevention enabled" if acquired else candidate.inhibitor.reason
            if not message:
                message = "Sleep prevention unavailable; keep the computer awake."
        except Exception:
            acquired = False
            message = "Sleep prevention unavailable; keep the computer awake."
        # Never hold the state lock during OS acquisition, cleanup or callback.
        with self._lock:
            candidate.completed = True
            candidate.acquired = acquired
            current = self._current is candidate
            if current and not acquired:
                self._current = None
        if not current or not acquired:
            self._release(candidate)
        if current:
            try:
                callback(message)
            except Exception:
                # The GUI may already have closed. Drop our owned lock without
                # printing callback exceptions or disturbing a newer candidate.
                with self._lock:
                    release = self._current is candidate
                    if release:
                        self._current = None
                if release:
                    self._release(candidate)

    @staticmethod
    def _release(candidate):
        try:
            candidate.inhibitor.stop()
        except Exception:
            pass

    def _release_later(self, candidate):
        threading.Thread(target=self._release, args=(candidate,), daemon=True).start()

    def stop(self) -> None:
        with self._lock:
            previous = self._current
            self._current = None
            release_previous = previous is not None and previous.completed
        if release_previous:
            self._release_later(previous)
