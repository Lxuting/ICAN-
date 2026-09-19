from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from .main_window import MainWindow
from .theme import MAIN_STYLE


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("钢智灵枢 · 智能钢铁仓储平台")
        self.resize(430, 330)
        self.setStyleSheet(MAIN_STYLE)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(55, 45, 55, 45)
        title = QLabel("钢智灵枢")
        title.setObjectName("title")
        title.setAlignment(0x84)
        sub = QLabel("面向钢铁仓储的多模态AI感知与智能决策软件平台")
        sub.setWordWrap(True)
        self.user = QLineEdit(); self.user.setPlaceholderText("用户名")
        self.pwd = QLineEdit(); self.pwd.setPlaceholderText("密码"); self.pwd.setEchoMode(QLineEdit.Password)
        btn = QPushButton("登录系统")
        btn.clicked.connect(self.login)
        layout.addWidget(title); layout.addWidget(sub); layout.addSpacing(18)
        layout.addWidget(self.user); layout.addWidget(self.pwd); layout.addSpacing(10); layout.addWidget(btn)

    def login(self):
        if not self.user.text():
            self.user.setText("admin")
        self.main = MainWindow()
        self.main.show()
        self.close()
