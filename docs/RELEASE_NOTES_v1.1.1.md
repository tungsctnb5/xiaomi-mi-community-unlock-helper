## Downloads

Choose the package for your computer. Both include Python and runtime dependencies.

| Platform | Download |
|---|---|
| Windows 10/11 x64 | [Windows ZIP](https://github.com/tungsctnb5/xiaomi-mi-community-unlock-helper/releases/download/v1.1.1/Xiaomi-Mi-Community-Unlock-Helper-Windows-x64.zip) |
| macOS 13+ on Apple Silicon (M1 or newer) | [macOS ZIP](https://github.com/tungsctnb5/xiaomi-mi-community-unlock-helper/releases/download/v1.1.1/Xiaomi-Mi-Community-Unlock-Helper-macOS-arm64.zip) |

## Adaptive Execution layout fix

- Attempt 1–4 inputs retain enough height and width to show the complete value, including the minus sign and `ms`.
- Four columns become two rows in compact windows; shorter windows scroll instead of squeezing the inputs.
- Clear, separate up/down buttons and fonts available on Windows.
- Layout checks on Windows at 100%, 125%, 150%, and 200% display scaling, plus an offline smoke test of the packaged executable.

## Installation / update

**Windows:** Close the previous app, extract the entire new ZIP into a fresh folder, then run `Xiaomi Mi Community Unlock Helper.exe`. Keep `_internal` next to the executable. If SmartScreen blocks the unsigned community build, use **More info → Run anyway** after checking the download source.

**macOS:** Quit the previous app, unzip the macOS package, and move `Xiaomi Mi Community Unlock Helper.app` to Applications. If blocked, use System Settings → Privacy & Security → **Open Anyway**.

Existing locally stored sessions are retained. Timing offsets and request behavior are unchanged by this layout update.

This helper submits Xiaomi's Mi Community authorization application; it does not unlock a phone directly or guarantee account eligibility or quota availability.

[Full changelog](https://github.com/tungsctnb5/xiaomi-mi-community-unlock-helper/compare/v1.1.0...v1.1.1)
