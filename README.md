# Xiaomi Mi Community Unlock Helper

A cross-platform desktop GUI for submitting a finite, precisely scheduled Xiaomi Global Mi Community bootloader authorization application. Available for **macOS Apple Silicon** and **Windows x64**.

It does **not** unlock a device by itself, bypass Xiaomi account eligibility, or guarantee quota availability. Use it only with your own Xiaomi account and devices.

## Download

Choose the package for your operating system from [GitHub Releases](https://github.com/tungsctnb5/xiaomi-mi-community-unlock-helper/releases/latest):

| Platform | Requirements | Package |
|---|---|---|
| macOS | Apple Silicon (M1 or newer), macOS 13+ | `Xiaomi-Mi-Community-Unlock-Helper-macOS-arm64.zip` |
| Windows | Windows 10/11 x64 | `Xiaomi-Mi-Community-Unlock-Helper-Windows-x64.zip` |

Python, PySide6, and all runtime dependencies are bundled in both packages.

### macOS

Unzip the macOS package and move the app to `/Applications`. If Gatekeeper blocks this community build, right-click the app and choose **Open**, or use System Settings → Privacy & Security → **Open Anyway**. Do not disable Gatekeeper globally.

### Windows

Unzip the **entire** Windows package, open its application folder, and launch `Xiaomi Mi Community Unlock Helper.exe`. If SmartScreen appears, choose **More info → Run anyway**. Do not move the `.exe` away from its `_internal` folder.

## Run / build

```bash
./build.sh
./run.sh
```

On Windows, run `build-windows.bat`. PyInstaller builds must run on their target operating system; the included GitHub Actions workflow provides a reproducible Windows builder.

The built app is `dist/Xiaomi Mi Community Unlock Helper.app`. It targets Apple Silicon. If Gatekeeper blocks this unsigned local build, right-click the app and choose **Open**, or use System Settings → Privacy & Security → Open Anyway. Do not disable Gatekeeper globally.

## Login and privacy

**Add / Login Xiaomi** opens an isolated in-app browser profile. You type credentials directly into Xiaomi's page; the helper never reads or stores the password. When Xiaomi sets `new_bbs_serviceToken`, the app stores it in macOS Keychain or Windows Credential Manager. **Logout Xiaomi** cancels waiting, deletes the stored token, and clears cookies/cache only from this isolated profile so another account can sign in. If Xiaomi changes its login flow or blocks embedded browsers, use **Paste Token Manually**; no `token.txt` is needed.

The token is sent only to `https://sgp-api.buy.mi.com` as required by the Xiaomi API. Logs mask it, telemetry is absent, and raw responses are locally displayed only after redaction. A random `deviceId` is generated once and persisted locally per app installation, because changing it per attempt adds session inconsistency without a demonstrated benefit.

## Operation

The app is LIVE-only and always requires a valid token before Start. Adaptive mode targets estimated Xiaomi server arrival at `-100, +20, +120, +300 ms` around Beijing midnight. Shortly before reset it re-syncs NTP, measures five state RTTs, estimates outbound delay, opens and warms four independent keep-alive channels, then computes local firing times. RTT/2 is only an estimate because internet routes may be asymmetric; the measured uncertainty is shown in logs. Disabling Adaptive uses the July 2026 fallback at 1400, 900, 400 and 100 ms before midnight.

Each firing dispatches its HTTP request to an independent worker, so a slow earlier response cannot delay a later target. Workers share one logical Xiaomi account session, token and stable device identity, while each owns a warmed network channel. Each Start creates at most four requests. Terminal replies stop targets that have not fired yet; requests already in flight cannot be recalled. `QUOTA FULL` does not cancel later attempts because an early request may still be observing the previous quota window. The app prevents system sleep while armed and releases that assertion on completion or Cancel. An accepted POST is labelled as accepted first, then the account state is queried again before authorization is called confirmed.

Use this only for your own account and device, within Xiaomi's terms and local law. Xiaomi can change undocumented APIs and response codes at any time.

## Tests

Tests use mock sessions and fake tokens only. They cover redaction, state/apply parsing, expiry, quota, NTP offset, four finite firings, cancellation, terminal stop, and timeout handling.
