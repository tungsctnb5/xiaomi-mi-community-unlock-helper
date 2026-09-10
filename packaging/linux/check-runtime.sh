#!/usr/bin/env bash
# Read-only dependency diagnostics using the same library directory as the app.
set -euo pipefail
app_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
failed=0
components=(
    'Xiaomi Mi Community Unlock Helper'
    '_internal/PySide6/Qt/libexec/QtWebEngineProcess'
    '_internal/PySide6/Qt/lib/libQt6WebEngineCore.so.6'
    '_internal/PySide6/Qt/lib/libQt6Widgets.so.6'
    '_internal/PySide6/Qt/plugins/platforms/libqxcb.so'
    '_internal/PySide6/Qt/plugins/xcbglintegrations/libqxcb-glx-integration.so'
)
for component in "${components[@]}"; do
    if [[ ! -e "$app_dir/$component" ]]; then
        echo "Missing packaged component: $component" >&2
        failed=1
        continue
    fi
    if ! links=$(LD_LIBRARY_PATH="$app_dir/_internal" ldd "$app_dir/$component" 2>&1); then
        echo "Could not inspect $component: $links" >&2
        failed=1
    elif missing=$(printf '%s\n' "$links" | grep -E 'not found|version .* not found'); then
        echo "Unresolved dependencies for $component:" >&2
        printf '%s\n' "$missing" >&2
        failed=1
    fi
done
if [[ $failed == 0 ]]; then
    echo "App, browser renderer, QtWidgets and XCB/GLX runtime links are available."
fi
exit "$failed"
