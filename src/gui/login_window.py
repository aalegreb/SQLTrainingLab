from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

class LoginWindow(QWidget):

    login_requested = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        # Título de ventana
        self.setWindowTitle("SQLTrainingLab - Login")
        self.setMinimumSize(400, 220)

        # Layout vertical
        layout = QVBoxLayout()

        # Título
        self._title = QLabel("SQLTrainingLab - Inicio de Sesión")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(self._title)

        # Campo username
        layout.addWidget(QLabel("Usuario:"))
        self._user_input = QLineEdit()
        layout.addWidget(self._user_input)

        # Campo password
        layout.addWidget(QLabel("Contraseña:"))
        self._password_input = QLineEdit()
        self._password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self._password_input)

        # Botón para confirmar
        self._login_button = QPushButton("Conectar")
        self._login_button.clicked.connect(self._handle_login)
        layout.addWidget(self._login_button)

        # Atajo para pasar a la contraseña
        self._user_input.returnPressed.connect(self._password_input.setFocus)

        # Atajo para confirmar
        self._password_input.returnPressed.connect(self._handle_login)

        # Empuja hacia arriba los elementos
        layout.addStretch()

        # Se establece el layout
        self.setLayout(layout)

    def _handle_login(self):
        user = self._user_input.text().strip()
        password = self._password_input.text()

        if not user or not password:
            QMessageBox.warning(self, "Error", "Por favor, completa los dos campos")
            return

        self.login_requested.emit(user, password)

    def clear_password_field(self):
        self._password_input.clear()
