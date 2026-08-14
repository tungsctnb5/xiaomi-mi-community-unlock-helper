import os
import subprocess
import sys
from pathlib import Path

APP_NAME = "Xiaomi Mi Community Unlock Helper"

def app_data_dir() -> Path:
    if sys.platform == "win32":
        root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return root / APP_NAME
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Xiaomi Unlock Helper"
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / APP_NAME

class SleepInhibitor:
    ES_CONTINUOUS=0x80000000; ES_SYSTEM_REQUIRED=0x00000001; ES_DISPLAY_REQUIRED=0x00000002
    def __init__(self): self.process=None; self.active=False
    def start(self):
        if self.active: return
        if sys.platform == "darwin":
            self.process=subprocess.Popen(["/usr/bin/caffeinate","-dimsu"])
        elif sys.platform == "win32":
            import ctypes
            ctypes.windll.kernel32.SetThreadExecutionState(self.ES_CONTINUOUS|self.ES_SYSTEM_REQUIRED|self.ES_DISPLAY_REQUIRED)
        self.active=True
    def stop(self):
        if not self.active: return
        if self.process and self.process.poll() is None: self.process.terminate()
        if sys.platform == "win32":
            import ctypes
            ctypes.windll.kernel32.SetThreadExecutionState(self.ES_CONTINUOUS)
        self.process=None; self.active=False
