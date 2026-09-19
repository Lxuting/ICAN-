import os
import sys

os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")

from PyQt5.QtWidgets import QApplication
from app.ui.login_window import LoginWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("钢智灵枢")
    app.setStyle("Fusion")
    login = LoginWindow()
    login.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
