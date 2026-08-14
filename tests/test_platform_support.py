from pathlib import Path
from app import platform_support

def test_windows_app_data(monkeypatch,tmp_path):
    monkeypatch.setattr(platform_support.sys,"platform","win32")
    monkeypatch.setenv("LOCALAPPDATA",str(tmp_path))
    assert platform_support.app_data_dir()==tmp_path/platform_support.APP_NAME

def test_windows_build_files_exist():
    root=Path(__file__).parents[1]
    assert (root/"XiaomiUnlockHelper-Windows.spec").exists()
    assert (root/".github/workflows/build-windows.yml").exists()
