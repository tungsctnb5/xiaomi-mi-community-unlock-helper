from pathlib import Path
from PySide6.QtCore import QTimer, QUrl, Signal
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWebEngineCore import QWebEngineProfile
from PySide6.QtWebEngineWidgets import QWebEngineView

# Start at Xiaomi Community's gateway. It creates the signed account.xiaomi.com
# callback; constructing that callback ourselves causes login-back to return 404.
LOGIN_URL = "https://sgp-api.buy.mi.com/bbs/api/global/user/login-in?callbackurl=https%3A%2F%2Fnew-ams.c.mi.com%2Fglobal%2F"

class LoginWindow(QMainWindow):
    token_found=Signal(str)
    def __init__(self, profile_dir:Path):
        super().__init__(); self.setWindowTitle("Xiaomi Login — private application profile"); self.resize(1000,760)
        self._captured=False
        self.profile=QWebEngineProfile("XiaomiUnlockHelper",self)
        self.profile.setPersistentStoragePath(str(profile_dir)); self.profile.setCachePath(str(profile_dir/"cache"))
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
        self.profile.cookieStore().cookieAdded.connect(self._cookie)
        self.view=QWebEngineView(); self.view.setPage(__import__('PySide6.QtWebEngineCore',fromlist=['QWebEnginePage']).QWebEnginePage(self.profile,self.view)); self.setCentralWidget(self.view)
        self.view.urlChanged.connect(lambda url:self.statusBar().showMessage(f"Xiaomi: {url.host()}"))
        self.view.loadFinished.connect(self._loaded)
        self.statusBar().showMessage("Opening Xiaomi Community sign-in…")
        self.view.load(QUrl(LOGIN_URL)); self.profile.cookieStore().loadAllCookies()
    def _cookie(self,cookie):
        if not self._captured and bytes(cookie.name()).decode(errors="ignore")=="new_bbs_serviceToken":
            value=bytes(cookie.value()).decode(errors="ignore")
            if value:
                self._captured=True; self.token_found.emit(value)
                self.setWindowTitle("Xiaomi Login — success")
                self.view.setHtml("""<html><body style='background:#171717;color:#eee;font:20px -apple-system;padding:40px'>
                  <h2 style='color:#65d46e'>Login successful</h2>
                  <p>The Xiaomi Community session token was saved securely to macOS Keychain.</p>
                  <p>This window will close automatically.</p></body></html>""")
                QTimer.singleShot(1800,self.close)
    def _loaded(self,ok):
        if not ok and not self._captured:
            self.statusBar().showMessage("Xiaomi page failed to load. Close and try again.")


def clear_browser_session(profile_dir: Path, parent=None):
    """Clear only the helper's isolated browser profile, never the user's browsers."""
    profile = QWebEngineProfile("XiaomiUnlockHelperLogout", parent)
    profile.setPersistentStoragePath(str(profile_dir))
    profile.setCachePath(str(profile_dir / "cache"))
    profile.cookieStore().deleteAllCookies()
    profile.clearHttpCache()
    profile.clearAllVisitedLinks()
    return profile
