# -*- mode: python ; coding: utf-8 -*-
"""Linux x86_64 one-directory build; Qt's hooks include the sandboxed renderer."""
import sys

from PyInstaller.utils.hooks import collect_submodules, copy_metadata

if sys.platform != "linux":
    raise SystemExit("Build the Linux package on Linux (see build-linux.sh).")

datas = [
    ("assets/app-icon-macos.png", "assets"),
    ("assets/chevron-up.svg", "assets"),
    ("assets/chevron-down.svg", "assets"),
]
# Backend discovery uses distribution entry points. SecretStorage talks to the
# desktop Secret Service through Jeepney; neither needs a system Python install.
datas += copy_metadata("keyring", recursive=True)
hiddenimports = [
    "PySide6.QtWebEngineCore",
    "PySide6.QtWebEngineWidgets",
    "keyring.backends.SecretService",
    "keyring.backends.chainer",
]
hiddenimports += collect_submodules("secretstorage")
hiddenimports += collect_submodules("jeepney")

a = Analysis(
    ["app/main.py"], pathex=["."], binaries=[], datas=datas,
    hiddenimports=hiddenimports, noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [], exclude_binaries=True,
    name="Xiaomi Mi Community Unlock Helper", console=False,
)
coll = COLLECT(
    exe, a.binaries, a.datas, strip=False, upx=False,
    name="Xiaomi Mi Community Unlock Helper",
)
