import os,sys
os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS","--disable-features=HttpsFirstBalancedModeAutoEnable")
from PySide6.QtGui import QIcon
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from app.gui.main_window import MainWindow
from app.gui.main_window import resource_path

def main():
    app=QApplication(sys.argv); app.setApplicationName("Xiaomi Mi Community Unlock Helper"); app.setApplicationDisplayName("Xiaomi Mi Community Unlock Helper"); app.setOrganizationName("Local"); app.setWindowIcon(QIcon(str(resource_path("app-icon-macos.png"))))
    smoke_test="--smoke-test" in sys.argv
    window=MainWindow(smoke_test=smoke_test); window.show()
    if smoke_test:
        # The frozen-build check never loads credentials or starts network tasks.
        def verify_layout():
            valid=len(window.offset_spins)==4
            for spin in window.offset_spins:
                spin.setValue(-2000)
                editor=spin.lineEdit(); metrics=editor.fontMetrics()
                valid=valid and editor.height()>=metrics.height()+2
                valid=valid and editor.width()>=metrics.horizontalAdvance(spin.text())+4
            window.close(); app.exit(0 if valid else 1)
        QTimer.singleShot(500,verify_layout)
    return app.exec()
if __name__=="__main__": raise SystemExit(main())
