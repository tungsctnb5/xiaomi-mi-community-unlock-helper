# Xiaomi Mi Community Unlock Helper

A cross-platform desktop GUI for submitting a finite, precisely scheduled Xiaomi Global Mi Community bootloader authorization application. Available for **macOS Apple Silicon**, **Windows x64**, and **Linux x64**.

It does **not** unlock a device by itself, bypass Xiaomi account eligibility, or guarantee quota availability. Use it only with your own Xiaomi account and devices.

## Download

Choose the package for your operating system from [GitHub Releases](https://github.com/tungsctnb5/xiaomi-mi-community-unlock-helper/releases/latest):

| Platform | Requirements | Package |
|---|---|---|
| macOS | Apple Silicon (M1 or newer), macOS 13+ | [Download macOS ZIP](https://github.com/tungsctnb5/xiaomi-mi-community-unlock-helper/releases/latest/download/Xiaomi-Mi-Community-Unlock-Helper-macOS-arm64.zip) |
| Windows | Windows 10/11 x64 | [Download Windows ZIP](https://github.com/tungsctnb5/xiaomi-mi-community-unlock-helper/releases/latest/download/Xiaomi-Mi-Community-Unlock-Helper-Windows-x64.zip) |
| Linux | Ubuntu 22.04 / 24.04 Desktop x64, X11 or XWayland | [Download Linux archive](https://github.com/tungsctnb5/xiaomi-mi-community-unlock-helper/releases/latest/download/Xiaomi-Mi-Community-Unlock-Helper-Linux-x64.tar.gz) |

Python and Python dependencies are bundled in all three packages. Linux uses the desktop's system libraries; see the Linux notes below.

### macOS

Unzip the macOS package and move the app to `/Applications`. If Gatekeeper blocks this community build, right-click the app and choose **Open**, or use System Settings → Privacy & Security → **Open Anyway**. Do not disable Gatekeeper globally.

### Windows

Unzip the **entire** Windows package, open its application folder, and launch `Xiaomi Mi Community Unlock Helper.exe`. If SmartScreen appears, choose **More info → Run anyway**. Do not move the `.exe` away from its `_internal` folder.

Version 1.1.1 fixes compressed Adaptive Execution inputs on Windows. Attempt values keep enough space for the full signed number and `ms`; compact windows use two rows, and shorter windows scroll. To update, close the old app and extract the new ZIP into a fresh folder, then launch that copy.

### Linux

Extract the entire `.tar.gz`, open a terminal in the extracted application folder and run `./launch.sh` as your normal desktop user. No Python installation is needed. Keep `_internal` alongside the executable.

The Linux x64 build targets Ubuntu 22.04 and 24.04, using X11/XWayland. Other glibc distributions may work but are not release-tested; this archive is not for Linux ARM64 or Alpine/musl. Minimal desktops may need system libraries such as `libxcb-cursor0`. The included [Linux instructions](packaging/linux/README-Linux.md) list dependencies and the optional per-application Ubuntu 24.04 browser-sandbox setup.

## Run / build

```bash
./build.sh
./run.sh
```

On Windows, run `build-windows.bat`. PyInstaller builds must run on their target operating system; the included GitHub Actions workflow provides a reproducible Windows builder.

On Linux x64, run `./build-linux.sh`. The **Build Linux** GitHub Actions workflow builds on Ubuntu 22.04 and verifies the same extracted archive on Ubuntu 24.04.

The built app is `dist/Xiaomi Mi Community Unlock Helper.app`. It targets Apple Silicon. If Gatekeeper blocks this unsigned local build, right-click the app and choose **Open**, or use System Settings → Privacy & Security → Open Anyway. Do not disable Gatekeeper globally.

## Login and privacy

**Add / Login Xiaomi** opens an isolated in-app browser profile. You type credentials directly into Xiaomi's page; the helper never reads or stores the password. When Xiaomi sets `new_bbs_serviceToken`, the app stores it in macOS Keychain, Windows Credential Manager, or the Linux desktop Secret Service (such as GNOME Keyring). **Logout Xiaomi** cancels waiting, deletes the stored token, and clears this isolated browser session. If the system credential store is locked or unavailable, the app reports that saving failed and lets you use the current session. Linux uses an off-the-record browser profile, so a missing keyring does not fall back to persistent cookie files. If Xiaomi changes its login flow or blocks embedded browsers, use **Paste Token Manually**; no `token.txt` is needed.

The token is sent only to `https://sgp-api.buy.mi.com` as required by the Xiaomi API. Logs mask it, telemetry is absent, and raw responses are locally displayed only after redaction. A random `deviceId` is generated once and persisted locally per app installation, because changing it per attempt adds session inconsistency without a demonstrated benefit.

## Operation

The app is LIVE-only and always requires a valid token before Start. Adaptive mode targets estimated Xiaomi server arrival at `-100, +20, +120, +300 ms` around Beijing midnight. Shortly before reset it re-syncs NTP, measures five state RTTs, estimates outbound delay, opens and warms four independent keep-alive channels, then computes local firing times. RTT/2 is only an estimate because internet routes may be asymmetric; the measured uncertainty is shown in logs. Disabling Adaptive uses the July 2026 fallback at 1400, 900, 400 and 100 ms before midnight.

Each firing dispatches its HTTP request to an independent worker, so a slow earlier response cannot delay a later target. Workers share one logical Xiaomi account session, token and stable device identity, while each owns a warmed network channel. Each Start creates at most four requests. Terminal replies stop targets that have not fired yet; requests already in flight cannot be recalled. `QUOTA FULL` does not cancel later attempts because an early request may still be observing the previous quota window. The app prevents system sleep while armed and releases that assertion on completion or Cancel. An accepted POST is labelled as accepted first, then the account state is queried again before authorization is called confirmed.

Use this only for your own account and device, within Xiaomi's terms and local law. Xiaomi can change undocumented APIs and response codes at any time.

## Tests

Tests use mock sessions and fake tokens only. They cover redaction, state/apply parsing, expiry, quota, NTP offset, four finite firings, cancellation, terminal stop, and timeout handling.

Windows builds also check the displayed layout at 100%, 125%, 150%, and 200% scaling, including window resizing, text visibility, and keyboard/step-button editing. The packaged executable runs an offline `--smoke-test` before it is archived; this check does not load credentials or contact Xiaomi/NTP.

Linux runs the same four-scale layout checks under X11. The extracted package is checked on Ubuntu 22.04 and 24.04 for GUI launch, sandboxed HTML rendering/JavaScript/HttpOnly-cookie capture, and a Secret Service roundtrip with synthetic data in an isolated temporary keyring. Mocked tests cover missing/locked storage, cancellation during Linux sleep-inhibitor acquisition, and cleanup.
