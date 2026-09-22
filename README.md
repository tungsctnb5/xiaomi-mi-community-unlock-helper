# Xiaomi Mi Community Unlock Helper

## English

An independently developed desktop application for scheduling Xiaomi Community Global bootloader-unlock permission applications. Available for **macOS Apple Silicon**, **Windows x64**, and **Linux x64**, with session management, time synchronization and up to four scheduled attempts.

No phone-model, device-generation or phone-OS selection is required: the helper submits an account-level application instead of interacting with a handset or its ROM. It is intended for eligible **Xiaomi, Redmi and POCO** users, including **MIUI and HyperOS** users where the Global Community authorization flow applies.

This does not guarantee compatibility or approval for every model, system version or region. Xiaomi controls eligibility, quotas and waiting periods; some MIUI devices may use the original unlock process instead. This helper does not implement the Mainland China application flow, unlock a phone itself or bypass Xiaomi's restrictions. Use it only with your own account and devices. [Xiaomi's eligibility guidance](https://www.mi.com/global/support/faq/details/KA-07238/).

## 简体中文

独立开发的桌面应用，用于定时提交小米社区国际版（Xiaomi Community Global）Bootloader 解锁资格申请。提供 **macOS Apple Silicon、Windows x64 和 Linux x64** 版本，支持会话管理、时间同步及最多四次定时申请。

无需选择手机型号、设备代际或手机操作系统：工具按小米账号提交申请，不直接操作手机或 ROM。面向符合申请条件的 **小米、Redmi 和 POCO** 用户，包括适用国际版社区授权流程的 **MIUI 和 HyperOS（小米澎湃 OS）** 用户。

这不代表所有机型、系统版本或地区都兼容或一定能通过审核。申请资格、名额和等待时间由小米决定；部分 MIUI 设备可能沿用原有解锁流程。本工具不提供中国大陆版申请流程，不直接解锁手机，也不绕过小米限制。请仅用于自己的账号和设备。[小米官方资格说明](https://www.mi.com/global/support/faq/details/KA-07238/)。

## Tiếng Việt

Ứng dụng desktop được phát triển độc lập, giúp hẹn giờ gửi đơn đăng ký quyền mở khóa bootloader qua Xiaomi Community Global. Có bản cho **macOS Apple Silicon**, **Windows x64** và **Linux x64**, với quản lý phiên đăng nhập, đồng bộ thời gian và tối đa bốn lượt gửi theo lịch.

Không cần chọn model, thế hệ máy hay hệ điều hành điện thoại: tool gửi yêu cầu ở cấp tài khoản, không thao tác trực tiếp với điện thoại hoặc ROM. Dành cho người dùng **Xiaomi, Redmi và POCO** đủ điều kiện, bao gồm **MIUI và HyperOS** khi quy trình cấp quyền của Xiaomi Community Global áp dụng.

Điều này không bảo đảm mọi model, phiên bản hệ điều hành hay khu vực đều tương thích hoặc được duyệt. Xiaomi quyết định điều kiện, hạn ngạch và thời gian chờ; một số máy MIUI có thể dùng quy trình unlock cũ. Tool không triển khai luồng đăng ký dành cho Trung Quốc đại lục, không tự mở khóa điện thoại và không vượt qua giới hạn của Xiaomi. Chỉ sử dụng với tài khoản và thiết bị của bạn. [Điều kiện từ Xiaomi](https://www.mi.com/global/support/faq/details/KA-07238/).

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

The app is LIVE-only and always requires a valid token before Start. **Measure Xiaomi Network** warms four independent keep-alive channels and collects exactly eight timed GET probes from Xiaomi's state endpoint; it never submits an application. The app rejects isolated stalls, reports p10/median/p90 RTT and jitter, then automatically fills four network-specific server-arrival targets and previews their estimated local send offsets. Stable connections keep a compact reset-window pattern, while variable connections receive a wider four-attempt spread.

A profile remains fresh for 15 minutes. If Start is pressed without one, the app measures automatically and continues to waiting when it succeeds. Shortly before reset it re-syncs NTP, samples Xiaomi again, warms the four live request channels and refreshes the recommendation before arming the scheduler. RTT/2 is only an outbound estimate because internet routes can be asymmetric; neither measurement nor timing can guarantee Xiaomi quota or approval. Disabling Adaptive uses the July 2026 fallback at 1400, 900, 400 and 100 ms before midnight.

Each firing dispatches its HTTP request to an independent worker, so a slow earlier response cannot delay a later target. Workers share one logical Xiaomi account session, token and stable device identity, while each owns a warmed network channel. Each Start creates at most four requests. Terminal replies stop targets that have not fired yet; requests already in flight cannot be recalled. `QUOTA FULL` does not cancel later attempts because an early request may still be observing the previous quota window. The app prevents system sleep while armed and releases that assertion on completion or Cancel. An accepted POST is labelled as accepted first, then the account state is queried again before authorization is called confirmed.

Use this only for your own account and device, within Xiaomi's terms and local law. Xiaomi can change undocumented APIs and response codes at any time.

## Tests

Tests use mock sessions and fake tokens only. They cover redaction, state/apply parsing, expiry, quota, NTP offset, robust network profiling, outlier rejection, stable/variable recommendations, GET-only measurement, exactly four finite firings, cancellation, terminal stop, and timeout handling.

Windows builds also check the displayed layout at 100%, 125%, 150%, and 200% scaling, including window resizing, text visibility, and keyboard/step-button editing. The packaged executable runs an offline `--smoke-test` before it is archived; this check does not load credentials or contact Xiaomi/NTP.

Linux runs the same four-scale layout checks under X11. The extracted package is checked on Ubuntu 22.04 and 24.04 for GUI launch, sandboxed HTML rendering/JavaScript/HttpOnly-cookie capture, and a Secret Service roundtrip with synthetic data in an isolated temporary keyring. Mocked tests cover missing/locked storage, cancellation during Linux sleep-inhibitor acquisition, and cleanup.

## About this project / 项目说明 / Về dự án

Developed and published by this project's author. This is an independent project, not a Xiaomi product.

本应用由项目作者开发并发布，是独立项目，并非小米公司出品。

Ứng dụng do tác giả dự án phát triển và phát hành. Đây là dự án độc lập, không phải sản phẩm do Xiaomi phát hành.
