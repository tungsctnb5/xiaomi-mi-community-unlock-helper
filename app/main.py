import os,sys
os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS","--disable-features=HttpsFirstBalancedModeAutoEnable")
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from app.gui.main_window import MainWindow
from app.gui.main_window import resource_path

def main():
    app=QApplication(sys.argv); app.setApplicationName("Xiaomi Mi Community Unlock Helper"); app.setApplicationDisplayName("Xiaomi Mi Community Unlock Helper"); app.setOrganizationName("Local"); app.setWindowIcon(QIcon(str(resource_path("app-icon-macos.png"))))
    window=MainWindow(); window.show(); return app.exec()
if __name__=="__main__": raise SystemExit(main())
