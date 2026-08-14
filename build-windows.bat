@echo off
setlocal
cd /d "%~dp0"
if not exist .venv-win\Scripts\python.exe py -3.13 -m venv .venv-win
.venv-win\Scripts\python.exe -m pip install -r requirements.txt
set QT_QPA_PLATFORM=offscreen
.venv-win\Scripts\python.exe -m pytest -q
if errorlevel 1 exit /b 1
.venv-win\Scripts\pyinstaller.exe --noconfirm --clean XiaomiUnlockHelper-Windows.spec
echo Built: %CD%\dist\Xiaomi Mi Community Unlock Helper\
