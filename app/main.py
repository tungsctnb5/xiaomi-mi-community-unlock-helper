import os,sys
os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS","--disable-features=HttpsFirstBalancedModeAutoEnable")
from PySide6.QtGui import QIcon
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from app.gui.main_window import MainWindow
from app.gui.main_window import resource_path

def main():
    if "--check-browser-sandbox" in sys.argv:
        from app.auth.linux_sandbox import namespace_probe
        return namespace_probe()
    if "--keyring-smoke-test" in sys.argv:
        from app.auth.store_smoke import run
        return run()
    app=QApplication(sys.argv); app.setApplicationName("Xiaomi Mi Community Unlock Helper"); app.setApplicationDisplayName("Xiaomi Mi Community Unlock Helper"); app.setOrganizationName("Local"); app.setWindowIcon(QIcon(str(resource_path("app-icon-macos.png"))))
    if "--webengine-smoke-test" in sys.argv:
        from app.gui.webengine_smoke import run
        return run(app)
    smoke_test="--smoke-test" in sys.argv
    window=MainWindow(smoke_test=smoke_test); window.show()
    if smoke_test:
        # The frozen-build check never loads credentials or starts network tasks.
        def verify_layout():
            valid=(window.start_btn.isVisible() and window.measure_btn.isVisible()
                   and not hasattr(window,"offset_spins")
                   and not hasattr(window,"adaptive"))
            window.close(); app.exit(0 if valid else 1)
        QTimer.singleShot(500,verify_layout)
    return app.exec()
if __name__=="__main__": raise SystemExit(main())
