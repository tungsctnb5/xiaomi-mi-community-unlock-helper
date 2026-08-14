# Xiaomi Mi Community Unlock Helper v1.1.0

## Download — choose your platform

- **macOS Apple Silicon (M1 or newer), macOS 13+:** `Xiaomi-Mi-Community-Unlock-Helper-macOS-arm64.zip`
- **Windows 10/11 x64:** `Xiaomi-Mi-Community-Unlock-Helper-Windows-x64.zip`

Python, PySide6, and runtime dependencies are bundled. You do not need to install Python.

### macOS installation

Unzip the package, move **Xiaomi Mi Community Unlock Helper.app** to Applications, then open it. Because this community build is not notarized, macOS may require right-click → **Open**, or System Settings → Privacy & Security → **Open Anyway**.

### Windows installation

Unzip the entire package and run **Xiaomi Mi Community Unlock Helper.exe** from its application folder. Keep the `_internal` folder beside the executable. If SmartScreen appears, choose **More info → Run anyway**.

## Highlights

- Native packages for macOS Apple Silicon and Windows x64.
- Adaptive four-channel timing around Beijing midnight.
- Four finite attempts—no infinite request loop.
- Local credential storage using macOS Keychain or Windows Credential Manager.
- Session validation, NTP synchronization, latency calibration, cancellation, redacted logs, and post-request verification.

This helper submits Xiaomi's Mi Community authorization application; it does not unlock a phone directly, bypass eligibility, or guarantee quota. Xiaomi APIs are undocumented and may change.

**Changes:** [v1.0.0...v1.1.0](https://github.com/tungsctnb5/xiaomi-mi-community-unlock-helper/compare/v1.0.0...v1.1.0)
