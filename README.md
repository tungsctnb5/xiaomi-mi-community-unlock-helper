# Xiaomi Mi Community Unlock Helper for macOS

A local-only macOS GUI for making a finite, scheduled Xiaomi Global bootloader authorization application. It does **not** unlock a device itself, bypass account eligibility, or guarantee Xiaomi quota availability.

## Download

Download the Apple Silicon ZIP from the repository's **Releases** page, unzip it, and move the app to `/Applications`. The current build supports Apple Silicon and macOS 13 or newer. It bundles Python and all runtime dependencies.

Windows x64 builds are produced on GitHub Actions and published as ZIP release assets. Unzip the complete folder and launch `Xiaomi Mi Community Unlock Helper.exe`; Python is not required. Windows may show a SmartScreen warning because community builds are not code-signed.

## Run / build

```bash
./build.sh
./run.sh
```

On Windows, run `build-windows.bat`. PyInstaller builds must run on their target operating system; the included GitHub Actions workflow provides the recommended reproducible Windows builder.

The built app is `dist/Xiaomi Mi Community Unlock Helper.app`. It targets Apple Silicon. If Gatekeeper blocks this unsigned local build, right-click the app and choose **Open**, or use System Settings → Privacy & Security → Open Anyway. Do not disable Gatekeeper globally.

## Login and privacy

**Add / Login Xiaomi** opens an isolated in-app browser profile. You type credentials directly into Xiaomi's page; the helper never reads or stores the password. When Xiaomi sets `new_bbs_serviceToken`, the app stores it in macOS Keychain. **Logout Xiaomi** cancels waiting, deletes the Keychain token, and clears cookies/cache only from this isolated profile so another account can sign in. If Xiaomi changes its login flow or blocks embedded browsers, use **Paste Token Manually**; no `token.txt` is needed.

The token is sent only to `https://sgp-api.buy.mi.com` as required by the Xiaomi API. Logs mask it, telemetry is absent, and raw responses are locally displayed only after redaction. A random `deviceId` is generated once and persisted locally per app installation, because changing it per attempt adds session inconsistency without a demonstrated benefit.

## Operation

The app is LIVE-only and always requires a valid token before Start. Adaptive mode targets estimated Xiaomi server arrival at `-100, +20, +120, +300 ms` around Beijing midnight. Shortly before reset it re-syncs NTP, measures five state RTTs, estimates outbound delay, opens and warms four independent keep-alive channels, then computes local firing times. RTT/2 is only an estimate because internet routes may be asymmetric; the measured uncertainty is shown in logs. Disabling Adaptive uses the July 2026 fallback at 1400, 900, 400 and 100 ms before midnight.

Each firing dispatches its HTTP request to an independent worker, so a slow earlier response cannot delay a later target. Workers share one logical Xiaomi account session, token and stable device identity, while each owns a warmed network channel. Each Start creates at most four requests. Terminal replies stop targets that have not fired yet; requests already in flight cannot be recalled. `QUOTA FULL` does not cancel later attempts because an early request may still be observing the previous quota window. The app prevents macOS sleep while armed and releases that assertion on completion or Cancel. An accepted POST is labelled as accepted first, then the account state is queried again before authorization is called confirmed.

Use this only for your own account and device, within Xiaomi's terms and local law. Xiaomi can change undocumented APIs and response codes at any time.

## Tests

Tests use mock sessions and fake tokens only. They cover redaction, state/apply parsing, expiry, quota, NTP offset, four finite firings, cancellation, terminal stop, and timeout handling.
