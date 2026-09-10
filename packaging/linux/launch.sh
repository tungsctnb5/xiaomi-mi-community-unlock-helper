#!/usr/bin/env bash
set -euo pipefail
app_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)

if [[ $EUID == 0 ]]; then
    echo "Open this desktop application as your normal user, without sudo." >&2
    exit 1
fi

# X11/XWayland is the tested rendering path. Respect an explicit Qt platform
# override, and allow native Wayland when no XWayland display is available.
if [[ -z "${QT_QPA_PLATFORM:-}" && -n "${DISPLAY:-}" ]]; then
    export QT_QPA_PLATFORM=xcb
fi
exec "$app_dir/Xiaomi Mi Community Unlock Helper" "$@"
