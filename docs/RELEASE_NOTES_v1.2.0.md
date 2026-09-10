## English

An independently developed desktop application for scheduling Xiaomi Community Global bootloader-unlock permission applications. Available for macOS Apple Silicon, Windows x64 and Linux x64.

Its account-based workflow requires no phone-model, generation or phone-OS selection. It is intended for eligible Xiaomi, Redmi and POCO users, including MIUI and HyperOS users where the Global authorization flow applies. It does not guarantee support or approval for every model, OS version or region, implement the Mainland China application flow, unlock phones itself or bypass Xiaomi's restrictions. Some MIUI devices may use the original unlock process instead. [Xiaomi's eligibility guidance](https://www.mi.com/global/support/faq/details/KA-07238/).

## 简体中文

独立开发的桌面应用，用于定时提交小米社区国际版（Xiaomi Community Global）Bootloader 解锁资格申请，提供 macOS Apple Silicon、Windows x64 和 Linux x64 版本。

工具按账号提交申请，无需选择手机型号、设备代际或手机操作系统。面向符合申请条件的小米、Redmi 和 POCO 用户，包括适用国际版授权流程的 MIUI 和 HyperOS（小米澎湃 OS）用户。不保证所有机型、系统版本或地区都受支持或能通过审核，不提供中国大陆版申请流程，不直接解锁手机，也不绕过小米限制。部分 MIUI 设备可能沿用原有解锁流程。[小米官方资格说明](https://www.mi.com/global/support/faq/details/KA-07238/)。

## Tiếng Việt

Ứng dụng desktop được phát triển độc lập, giúp hẹn giờ đăng ký quyền mở khóa bootloader qua Xiaomi Community Global, có bản cho macOS Apple Silicon, Windows x64 và Linux x64.

Tool gửi yêu cầu ở cấp tài khoản, không cần chọn model, thế hệ máy hay hệ điều hành điện thoại. Dành cho người dùng Xiaomi, Redmi và POCO đủ điều kiện, gồm MIUI và HyperOS khi luồng cấp quyền Global áp dụng. Không bảo đảm mọi model, phiên bản OS hay khu vực đều được hỗ trợ hoặc được duyệt; không triển khai luồng đăng ký Trung Quốc đại lục, không tự unlock điện thoại và không vượt giới hạn của Xiaomi. Một số máy MIUI có thể dùng quy trình unlock cũ. [Điều kiện từ Xiaomi](https://www.mi.com/global/support/faq/details/KA-07238/).

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

## About this project / 项目说明 / Về dự án

Developed and published by this project's author. This is an independent project, not a Xiaomi product.

本应用由项目作者开发并发布，是独立项目，并非小米公司出品。

Ứng dụng do tác giả dự án phát triển và phát hành. Đây là dự án độc lập, không phải sản phẩm do Xiaomi phát hành.

[Full changelog](https://github.com/tungsctnb5/xiaomi-mi-community-unlock-helper/compare/v1.1.1...v1.2.0)
