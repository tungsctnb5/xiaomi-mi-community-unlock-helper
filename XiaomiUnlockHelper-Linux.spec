# -*- mode: python ; coding: utf-8 -*-
"""Linux x86_64 one-directory build; Qt's hooks include the sandboxed renderer."""
import sys
from pathlib import Path

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
# Mesa/graphics drivers come from the target desktop and may need a newer C++
# ABI than the Ubuntu 22.04 builder. Keep GCC runtimes with that driver stack.
# https://pyinstaller.org/en/stable/usage.html#making-gnu-linux-apps-forward-compatible
a.binaries = [
    entry for entry in a.binaries
    if not Path(entry[0]).name.startswith(("libstdc++.so", "libgcc_s.so"))
]
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [], exclude_binaries=True,
    name="Xiaomi Mi Community Unlock Helper", console=False,
)
coll = COLLECT(
    exe, a.binaries, a.datas, strip=False, upx=False,
    name="Xiaomi Mi Community Unlock Helper",
)
