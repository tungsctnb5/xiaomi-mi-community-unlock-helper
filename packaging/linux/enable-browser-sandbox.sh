#!/usr/bin/env bash
# Optional, path-scoped Ubuntu 24.04+ AppArmor permission for Chromium's sandbox.
# This helper does not start the GUI or modify global kernel sandbox settings.
set -euo pipefail
app_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)

if [[ $EUID != 0 ]]; then
    echo "Run this helper once with sudo if Ubuntu blocks the login browser sandbox." >&2
    echo "Then open launch.sh normally, without sudo." >&2
    exit 1
fi
command -v apparmor_parser >/dev/null || { echo "AppArmor tools are not installed." >&2; exit 1; }
app_path="$app_dir/Xiaomi Mi Community Unlock Helper"
renderer_path="$app_dir/_internal/PySide6/Qt/libexec/QtWebEngineProcess"
[[ -x "$app_path" && -x "$renderer_path" ]] || { echo "Keep this helper inside the complete extracted app folder." >&2; exit 1; }

# AppArmor interprets glob/meta characters even inside quoted attachments.
# Reject unusual directory names rather than granting broader permissions.
case "$app_dir" in
    *[\"\'\\\{\}\[\]\*\?\^]*|*$'\n'*|*$'\r'*)
        echo "Move the app to a path without quotes, backslashes, newlines or glob characters first." >&2
        exit 1 ;;
esac

profile_path=/etc/apparmor.d/xiaomi-mi-community-unlock-helper
profile_tmp=$(mktemp)
trap 'rm -f -- "$profile_tmp"' EXIT
printf 'abi <abi/4.0>,\ninclude <tunables/global>\n\nprofile xiaomi-mi-community-unlock-helper "%s" flags=(unconfined) {\n  userns,\n}\n\nprofile xiaomi-mi-community-unlock-helper-renderer "%s" flags=(unconfined) {\n  userns,\n}\n' "$app_path" "$renderer_path" > "$profile_tmp"
apparmor_parser --skip-kernel-load "$profile_tmp"
if [[ -e "$profile_path" ]]; then
    # AppArmor ignores .bak files when loading its profile directory.
    backup_path="${profile_path}.$(date +%Y%m%d%H%M%S).bak"
    cp -p -- "$profile_path" "$backup_path"
    echo "Previous profile backed up to $backup_path"
fi
install -m 644 "$profile_tmp" "$profile_path"
apparmor_parser -r "$profile_path"
echo "Allowed Chromium user namespaces only for this app and its renderer: $app_dir"
echo "Open ./launch.sh as your normal user. If you move this folder, rerun this helper."
