#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

if [[ "$(uname -s)" != Linux || "$(uname -m)" != x86_64 ]]; then
    echo "Build this package on Linux x86_64, or use GitHub Actions: Build Linux." >&2
    exit 1
fi

if [[ "${1:-}" == --ci ]]; then
    # CI has already installed dependencies and run unit/native layout tests.
    build_python=python
elif [[ $# == 0 ]]; then
    [[ -x .venv-linux/bin/python ]] || python3 -m venv .venv-linux
    build_python=.venv-linux/bin/python
    "$build_python" -m pip install -r requirements.txt
    QT_QPA_PLATFORM=offscreen "$build_python" -m pytest -q --ignore=tests/test_execution_layout.py
else
    echo "Usage: ./build-linux.sh [--ci]" >&2
    exit 2
fi

"$build_python" -m PyInstaller --noconfirm --clean XiaomiUnlockHelper-Linux.spec
package_dir='dist/Xiaomi Mi Community Unlock Helper'
install -m 755 packaging/linux/launch.sh "$package_dir/launch.sh"
install -m 755 packaging/linux/enable-browser-sandbox.sh "$package_dir/enable-browser-sandbox.sh"
install -m 644 packaging/linux/README-Linux.md "$package_dir/README-Linux.md"
tar -C dist -czf dist/Xiaomi-Mi-Community-Unlock-Helper-Linux-x64.tar.gz 'Xiaomi Mi Community Unlock Helper'
(
    cd dist
    sha256sum Xiaomi-Mi-Community-Unlock-Helper-Linux-x64.tar.gz > Xiaomi-Mi-Community-Unlock-Helper-Linux-x64.tar.gz.sha256
)
echo "Built: $PWD/dist/Xiaomi-Mi-Community-Unlock-Helper-Linux-x64.tar.gz"
