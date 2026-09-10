## Downloads — macOS, Windows and Linux

| Platform | Download |
|---|---|
| Linux x64 — Ubuntu 22.04 / 24.04 Desktop | [Linux archive](https://github.com/tungsctnb5/xiaomi-mi-community-unlock-helper/releases/download/v1.2.0/Xiaomi-Mi-Community-Unlock-Helper-Linux-x64.tar.gz) |
| Windows 10/11 x64 | [Windows ZIP](https://github.com/tungsctnb5/xiaomi-mi-community-unlock-helper/releases/download/v1.2.0/Xiaomi-Mi-Community-Unlock-Helper-Windows-x64.zip) |
| macOS 13+ — Apple Silicon | [macOS ZIP](https://github.com/tungsctnb5/xiaomi-mi-community-unlock-helper/releases/download/v1.2.0/Xiaomi-Mi-Community-Unlock-Helper-macOS-arm64.zip) |

Python and Python dependencies are included in every download.

## New in v1.2.0

- Linux x64 portable package, built on Ubuntu 22.04 and checked on Ubuntu 24.04.
- Linux Secret Service credential storage (for example GNOME Keyring), with session-only use when storage is unavailable.
- Linux browser cookies/cache stay in memory; the token persists only in the secure desktop keyring.
- Linux sleep prevention with cancellation cleanup and a visible status when the desktop denies inhibition.
- Sandboxed embedded login browser, with an optional app-specific AppArmor setup helper for Ubuntu 24.04.
- Clearer credential-storage messages on every platform and the adaptive field layout fixes from v1.1.1.

## Install / update

**Linux:** Extract the whole `.tar.gz`, then run `./launch.sh` inside the extracted folder as your normal user. Keep `_internal` next to the executable. X11/XWayland is the tested display path. System libraries may need installing on minimal desktops; [Linux instructions](https://github.com/tungsctnb5/xiaomi-mi-community-unlock-helper/blob/v1.2.0/packaging/linux/README-Linux.md) are included in the package. This build is x86_64/glibc, not ARM64 or Alpine/musl.

**Windows:** Close the old app, extract the whole ZIP into a new folder and run the `.exe`. Keep `_internal`. An unsigned-build SmartScreen prompt may require **More info → Run anyway**.

**macOS:** Quit the old app, unzip and move the app to Applications. If blocked, use System Settings → Privacy & Security → **Open Anyway**.

## Verification

Mocked unit tests, native Linux/Windows layouts at 100–200% scaling, and packaged GUI smoke tests. Linux additionally checks the sandboxed renderer, synthetic HttpOnly-cookie capture and an isolated synthetic keyring roundtrip on both supported Ubuntu versions. No real Xiaomi account was used for these checks.

The helper submits Xiaomi's authorization application; Xiaomi still controls account eligibility, quota and device waiting periods.

[Full changelog](https://github.com/tungsctnb5/xiaomi-mi-community-unlock-helper/compare/v1.1.1...v1.2.0)
