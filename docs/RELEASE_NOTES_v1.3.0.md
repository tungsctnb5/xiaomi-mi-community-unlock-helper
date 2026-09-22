## English

Version 1.3.0 adds automatic Xiaomi network profiling. **Measure Xiaomi Network** uses finite GET-only probes against Xiaomi's state endpoint, filters isolated stalls and calculates four connection-specific timing values from measured RTT and jitter. Pressing Start without a fresh profile performs the measurement automatically, then continues to waiting. The app refreshes the recommendation close to Beijing midnight before arming four independent request channels.

No application is submitted during measurement. RTT/2 is an estimate—not a guarantee—because internet paths can be asymmetric and Xiaomi controls server processing, eligibility and quota.

## 简体中文

v1.3.0 新增小米网络自动测量功能。点击 **Measure Xiaomi Network** 后，应用只通过有限次数的 GET 请求测量小米状态接口，过滤偶发的异常延迟，并根据实际 RTT 和抖动自动计算四个适合当前网络的时间参数。若在没有有效测量结果时点击 Start，应用会先自动测量，再进入等待状态。接近北京时间零点时，应用会再次测量并更新建议值，然后启用四条独立请求通道。

测量过程不会提交解锁资格申请。由于网络路径可能不对称，RTT/2 只是估算值；小米仍决定服务器处理、申请资格和名额。

## Tiếng Việt

Phiên bản 1.3.0 bổ sung chức năng tự động đo đường truyền tới Xiaomi. Nút **Measure Xiaomi Network** chỉ gửi hữu hạn các request GET tới endpoint kiểm tra trạng thái, loại bỏ những mẫu trễ bất thường và tự tính bốn thông số timing phù hợp với RTT cùng độ dao động của mạng hiện tại. Nếu bấm Start khi chưa có kết quả còn hiệu lực, ứng dụng sẽ tự đo rồi chuyển sang trạng thái chờ. Gần 00:00 giờ Bắc Kinh, ứng dụng đo lại và cập nhật thông số trước khi kích hoạt bốn kênh request độc lập.

Bước đo không gửi đơn đăng ký. RTT/2 chỉ là giá trị ước lượng vì đường truyền có thể bất đối xứng; Xiaomi vẫn quyết định xử lý phía máy chủ, điều kiện tài khoản và hạn ngạch.

## Downloads

| Platform | Download |
|---|---|
| macOS 13+ — Apple Silicon | [macOS ZIP](https://github.com/tungsctnb5/xiaomi-mi-community-unlock-helper/releases/download/v1.3.0/Xiaomi-Mi-Community-Unlock-Helper-macOS-arm64.zip) |
| Windows 10/11 x64 | [Windows ZIP](https://github.com/tungsctnb5/xiaomi-mi-community-unlock-helper/releases/download/v1.3.0/Xiaomi-Mi-Community-Unlock-Helper-Windows-x64.zip) |
| Linux x64 — Ubuntu 22.04 / 24.04 Desktop | [Linux archive](https://github.com/tungsctnb5/xiaomi-mi-community-unlock-helper/releases/download/v1.3.0/Xiaomi-Mi-Community-Unlock-Helper-Linux-x64.tar.gz) |

Python and Python dependencies are included. Builds remain unsigned. No real Xiaomi account was used in automated tests.

## Verification

- Network profile tests cover stable and unstable paths, outlier rejection, insufficient samples, cancellation, expired sessions and the four-attempt upper bound.
- A source-level fake client verifies four warm-up GETs plus exactly eight timed GETs and fails if measurement attempts an apply POST.
- Full mocked tests, responsive layout tests and packaged smoke tests run before release.
- Linux is built on Ubuntu 22.04 and the same archive is verified on Ubuntu 24.04.

[Full changelog](https://github.com/tungsctnb5/xiaomi-mi-community-unlock-helper/compare/v1.2.0...v1.3.0)
