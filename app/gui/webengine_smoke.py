"""Exercise the packaged login renderer and HttpOnly cookie capture without network."""

from pathlib import Path

from PySide6.QtCore import QTimer, QUrl
from PySide6.QtNetwork import QNetworkCookie

from app.auth.browser import LoginWindow


def run(app):
    window = LoginWindow(Path("unused-offline-profile"), offline=True)
    expected = "fake-offline-smoke-session"
    finished = False

    def finish(ok):
        nonlocal finished
        if finished:
            return
        finished = True
        window.close()
        app.exit(0 if ok else 1)

    def captured(value):
        QTimer.singleShot(0, lambda: finish(value == expected and window.profile.isOffTheRecord()))

    def check_page(text):
        if text != "Offline renderer ready":
            finish(False)
            return
        cookie = QNetworkCookie(b"new_bbs_serviceToken", expected.encode())
        cookie.setHttpOnly(True)
        cookie.setSecure(True)
        cookie.setDomain("offline.invalid")
        cookie.setPath("/")
        window.profile.cookieStore().setCookie(cookie, QUrl("https://offline.invalid/"))

    def loaded(ok):
        if window._captured:
            return
        if not ok:
            finish(False)
            return
        window.view.page().runJavaScript("document.getElementById('probe').textContent", check_page)

    window.token_found.connect(captured)
    window.view.loadFinished.connect(loaded)
    window.view.page().renderProcessTerminated.connect(lambda *_: finish(False))
    QTimer.singleShot(15000, lambda: finish(False))
    window.show()
    result = app.exec()
    # Delete the page before its parent-owned profile.
    window.view.close()
    return result if finished else 1
