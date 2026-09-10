# Xiaomi Mi Community Unlock Helper — Linux

This is the Linux x86_64 package for Ubuntu 22.04/24.04 Desktop and compatible
glibc-based distributions. It bundles Python, PySide6, Qt WebEngine, and the
Python keyring dependencies. No Python or pip installation is needed to run it.
Other distributions are not release-tested; Linux ARM64 and musl/Alpine are not
supported by this archive. The build baseline is Ubuntu 22.04 (glibc 2.35).

## Open the app

Extract the complete `.tar.gz` archive. Open a terminal in the extracted
`Xiaomi Mi Community Unlock Helper` folder and run:

```bash
./launch.sh
```

Keep the `_internal` folder alongside the executable. Run as your normal desktop
user, without `sudo`. X11 or XWayland is the tested display path; the launcher
selects XWayland when it is available. Native Wayland is not release-tested.

## Desktop libraries

A normal Ubuntu Desktop usually already has most of these libraries. If the app
reports missing shared libraries or cannot load the `xcb` plugin, install:

```bash
sudo apt update
sudo apt install libxcb-cursor0 libxkbcommon-x11-0 libxcb-icccm4 \
  libxcb-image0 libxcb-keysyms1 libxcb-render-util0 libxcb-xinerama0 \
  libxcb-randr0 libxcb-shape0 libxcb-sync1 libxcb-xfixes0 libxcb-xkb1 \
  libxcb-shm0 libxcb-glx0 libx11-xcb1 libxrender1 libxi6 libxcomposite1 \
  libxdamage1 libxrandr2 libxtst6 libnss3 libnspr4 libdbus-1-3 \
  libfontconfig1 libfreetype6 libgl1 libegl1 libgbm1 libdrm2 libxshmfence1 \
  xdg-utils xwayland
```

Qt WebEngine also needs ALSA: `sudo apt install libasound2` on Ubuntu 22.04, or
`sudo apt install libasound2t64` on Ubuntu 24.04. Package names can differ on other
distributions. A graphical desktop, session D-Bus, and desktop Secret Service
(for example GNOME Keyring) are needed for persistent credential storage.

## Token storage

Tokens remain local. The app uses the desktop Secret Service keyring when it is
available; no plaintext token file is created. If no secure keyring is available,
the app offers session-only use and you will need to log in again after closing
it. On GNOME, unlock your login keyring when prompted. Minimal installations
may need `sudo apt install gnome-keyring dbus-user-session` and a desktop logout
and login. Never paste a real token into terminal commands or GitHub issues.

## Ubuntu 24.04 browser sandbox

Qt WebEngine uses Chromium's Linux sandbox. It needs unprivileged user namespaces
and seccomp. Ubuntu 24.04 can deny user namespaces to unpacked applications via
AppArmor. If clicking **Add / Login Xiaomi** fails with a sandbox/user-namespace
error, run the included helper once from the extracted app directory:

```bash
sudo ./enable-browser-sandbox.sh
```

It installs an AppArmor rule for the exact app and renderer paths in this folder.
It does not disable Chromium's sandbox or change global kernel settings. Existing
rules at the helper's named profile are backed up before replacement. After this,
run `./launch.sh` normally. Rerun the helper if you move the folder. If a managed
computer prohibits user namespaces, use **Paste Token Manually** instead.

## Verify the downloaded build without logging in

These checks use no account data and make no Xiaomi requests:

```bash
./launch.sh --smoke-test
./launch.sh --webengine-smoke-test
```

The second command renders an embedded local HTML page and checks JavaScript in
the bundled browser. It therefore also checks its resources and renderer.

## Build and compatibility references

- [PySide6 Essentials 6.11.1 wheels](https://pypi.org/project/PySide6-Essentials/6.11.1/#files)
  and [Addons wheels](https://pypi.org/project/PySide6-Addons/6.11.1/#files):
  Linux x86_64 wheels require glibc 2.34 or later. Building on Ubuntu 22.04 adds
  the glibc 2.35 baseline for this packaged executable.
- [Qt Linux dependencies](https://doc.qt.io/qt-6/linux-requirements.html).
- [Qt WebEngine sandbox requirements](https://doc.qt.io/qt-6/qtwebengine-platform-notes.html#sandboxing-support).
- [Ubuntu's per-application user namespace policy](https://ubuntu.com/blog/ubuntu-23-10-restricted-unprivileged-user-namespaces).
