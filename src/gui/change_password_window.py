from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from core.db_session import DatabaseSession
from utils.error_handling import handle_app_errors
from utils.logger import log
from utils.password_utils import (
    SPECIAL,
    is_valid_password,
    change_user_password
)

class ChangePasswordWindow(QWidget):

    password_changed = pyqtSignal()

    def __init__(self, db_session: DatabaseSession):
        super().__init__()
        self._db_session = db_session
        self._init_ui()

    def _init_ui(self):
        # Título de ventana
        self.setWindowTitle("SQLTrainingLab - Change Password")
        self.setMinimumSize(480, 280)

        # Layout vertical
        layout = QVBoxLayout()

        # Título
        self._title = QLabel("SQLTrainingLab - Cambio de contraseña")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(self._title)

        # Requisitos de la contraseña
        text = (
            f"La contraseña debe ser de al menos 12 caracteres y contener al "
            f"menos una mayúscula, una minúscula, un dígito y uno de los "
            f"siguientes caracteres:\n{SPECIAL}"
        )
        self._requirements = QLabel(text)
        self._requirements.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self._requirements.setWordWrap(True)
        layout.addWidget(self._requirements)

        # Campo contraseña
        layout.addWidget(QLabel("Nueva contraseña:"))
        self._password_input = QLineEdit()
        self._password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self._password_input)

        # Campo confirmar contraseña
        layout.addWidget(QLabel("Confirmar contraseña:"))
        self._confirm_input = QLineEdit()
        self._confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self._confirm_input)

        # Botón para guardar
        self._save_button = QPushButton("Guardar nueva contraseña")
        self._save_button.clicked.connect(self._check_new_password)
        layout.addWidget(self._save_button)

        # Atajos con Enter
        self._password_input.returnPressed.connect(self._confirm_input.setFocus)
        self._confirm_input.returnPressed.connect(self._check_new_password)

        # Empuja hacia arriba los elementos
        layout.addStretch()

        # Se establece el layout
        self.setLayout(layout)

    @handle_app_errors
    def _check_new_password(self, _ignored = False):
        new_password = self._password_input.text()
        confirm_password = self._confirm_input.text()

        if not new_password or not confirm_password:
            msg = "Por favor, completa los dos campos"
            QMessageBox.warning(self, "Error", msg)
            return

        if new_password != confirm_password:
            msg = "Las contraseñas no coinciden."
            QMessageBox.critical(self, "Error", msg)
            self._reset_window()
            return

        if not is_valid_password(new_password):
            msg = "La contraseña no cumple los requisitos mencionados."
            QMessageBox.critical(self, "Error", msg)
            self._reset_window()
            return

        change_user_password(
            self._db_session.get_real_connection(),
            self._db_session.get_username(),
            new_password
        )

        log("Contraseña cambiada desde GUI")
        self.password_changed.emit()

    def _reset_window(self):
        self._password_input.clear()
        self._confirm_input.clear()
