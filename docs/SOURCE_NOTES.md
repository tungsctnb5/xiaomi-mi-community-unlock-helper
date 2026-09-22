# Source review (July 2026)

Reviewed 2026-08-13:

- `2shrestha22/bootloader-unlock-req.py`, gist `3b0f76c37c1775f7b9ec693461b7aa82`, shown by GitHub as last active 2026-07-09. A snapshot is retained in `vendor/` for audit.
- `pwnj/auto-hyperos-unlocker`, current default branch, retained in `vendor/auto-hyperos-unlocker/`.

Observed community protocol:

- State endpoint: `GET https://sgp-api.buy.mi.com/bbs/api/global/user/bl-switch/state`.
- Apply endpoint: `POST https://sgp-api.buy.mi.com/bbs/api/global/apply/bl-auth` with compact semantic body `{"is_retry": true}`.
- Cookie fields: `new_bbs_serviceToken`, `versionCode=500411`, `versionName=5.4.11`, and a 40-character uppercase SHA-1-shaped random `deviceId`.
- POST headers include JSON UTF-8, `okhttp/4.12.0`, keep-alive and compression. This app excludes Brotli from Accept-Encoding unless a Brotli decoder is installed.
- State code `100004` means expired session. `is_pass=4/button_state=1` is eligible; button 2 is blocked until a deadline; button 3 is reported by the source as an account under 30 days; `is_pass=1` is already authorized.
- Apply `code=0`: `apply_result=1` accepted, `3` quota full, `4` blocked. Code `100003` is ambiguous and triggers verification. HTTP 200 alone is never treated as success.
- The source queries NTP transmit time once and extrapolates it with a wall clock. This app samples several servers, selects low-delay observations, applies the NTP offset, and extrapolates with a monotonic clock.
- `timeshift.txt` contains `1400, 900, 400, 100`; the code computes `next Beijing midnight - timeshift`, so these are pre-midnight offsets.
- The source creates a fresh random device ID each execution. The helper persists one locally to keep a single app profile/session identity stable; no evidence in the sources establishes that per-request rotation is required.
- The source's unbounded `while True` apply loop is intentionally not retained. The helper schedules exactly four attempts and stops on terminal results.

Undocumented API warning: response meanings beyond those observed above may change. Unknown payloads are preserved in credential-redacted debug logs instead of being guessed as success.

## Network-specific timing (v1.3.0)

This is an application improvement, not a behavior copied from the community loop. A manual measurement—or Start when no fresh profile exists—creates four keep-alive channels, warms each once, then performs two timed GET rounds for eight measured samples. It never calls the apply endpoint. The profile removes isolated stalls, calculates p10/median/p90 RTT and robust median-absolute-deviation jitter, estimates outbound time as median RTT/2, and widens the four reset-boundary targets when the path is variable. The number of live apply attempts remains exactly four.

The profile is refreshed close to Beijing midnight using the final state checks and warmed live channels. RTT/2 cannot reveal route asymmetry or Xiaomi's internal queue time, so the UI labels it as an estimate and does not promise an exact server-arrival timestamp.

Since v1.3.1 these timing targets are internal. The GUI deliberately has no editable timing fields or adaptive/fallback switch: Start always obtains a fresh measured profile, while the activity log retains the computed values for diagnosis.

## Login callback correction

The app begins login at Xiaomi Community's `user/login-in?callbackurl=...` gateway. The gateway returns a redirect containing Xiaomi's current signed `login-back` callback. A direct handcrafted Account login callback can authenticate the Xiaomi identity but fails the BBS token exchange with `404 page not found` because its gateway signature/context is missing.
