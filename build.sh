#!/bin/zsh
set -e
cd "${0:A:h}"
[[ -x .venv/bin/python ]] || python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q
.venv/bin/pyinstaller --noconfirm --clean XiaomiUnlockHelper.spec
echo "Built: $PWD/dist/Xiaomi Mi Community Unlock Helper.app"
