# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
datas=[("assets/app-icon-macos.png","assets")]; binaries=[]; hiddenimports=[]
for pkg in ("PySide6.QtWebEngineCore","PySide6.QtWebEngineWidgets","keyring.backends.Windows"):
    d,b,h=collect_all(pkg); datas+=d; binaries+=b; hiddenimports+=h
a=Analysis(["app/main.py"],pathex=["."],binaries=binaries,datas=datas,hiddenimports=hiddenimports,noarchive=False)
pyz=PYZ(a.pure)
exe=EXE(pyz,a.scripts,[],exclude_binaries=True,name="Xiaomi Mi Community Unlock Helper",console=False,icon="assets/AppIcon.ico")
coll=COLLECT(exe,a.binaries,a.datas,strip=False,upx=False,name="Xiaomi Mi Community Unlock Helper")
