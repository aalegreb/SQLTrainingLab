from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
    QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal

from admin_tools.setup_database import setup_database
from admin_tools.data_exporting import export_audit_data
from admin_tools.user_creation import create_users_from_excel
from core.db_session import DatabaseSession
from utils.error_handling import handle_app_errors
from utils.logger import log

class AdminToolsWindow(QWidget):

    enter_app_clicked = pyqtSignal()

    def __init__(self, db_session: DatabaseSession):
        super().__init__()
        self._db_session = db_session
        self._init_ui()

    def _init_ui(self):
        # Título de ventana
        self.setWindowTitle("SQLTrainingLab - Admin Tools")
        self.setMinimumSize(350, 200)

        # Layout vertical
        layout = QVBoxLayout()

        # Título
        self._title = QLabel("Bienvenido, administrador,\n¿qué desea hacer?")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self._title)

        # Botón Setup
        self._setup_button = QPushButton("Setup de la Base de Datos")
        self._setup_button.clicked.connect(self._on_clicked_setup)
        layout.addWidget(self._setup_button)

        # Botón Crear usuarios
        self._create_users_button = QPushButton("Crear usuarios")
        self._create_users_button.clicked.connect(self._on_clicked_create)
        layout.addWidget(self._create_users_button)

        # Botón Exportar datos Auditoría
        self._export_audit_button = QPushButton("Exportar datos de auditoría")
        self._export_audit_button.clicked.connect(self._on_clicked_export)
        layout.addWidget(self._export_audit_button)

        # Botón Acceder a la App
        self._enter_app_button = QPushButton("Acceder a SQLTrainingLab")
        self._enter_app_button.clicked.connect(self._on_clicked_enter)
        layout.addWidget(self._enter_app_button)

        # Empuja hacia arriba los elementos
        layout.addStretch()

        # Se establece el layout
        self.setLayout(layout)

    def _on_clicked_setup(self):
        self._run_admin_tool(
            running_msg = (
                "Ejecutando Setup inicial de la Base de Datos.\n"
                "Espera unos segundos..."
            ),
            admin_tool = setup_database
        )

    def _on_clicked_create(self):
        self._run_admin_tool(
            running_msg = (
                "Creando usuarios a partir del archivo Excel.\n"
                "Espera unos segundos..."
            ),
            admin_tool = create_users_from_excel
        )

    def _on_clicked_export(self):
        self._run_admin_tool(
            running_msg = (
                "Exportando datos de auditoría.\n"
                "Espera unos segundos..."
            ),
            admin_tool = export_audit_data
        )

    def _on_clicked_enter(self):
        self.enter_app_clicked.emit()

    @handle_app_errors
    def _run_admin_tool(self, running_msg: str, admin_tool):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("SQLTrainingLab - Admin")
        msg_box.setText(running_msg)
        msg_box.setStandardButtons(QMessageBox.StandardButton.NoButton)
        msg_box.show()

        QApplication.processEvents()

        log(f"Mostrada ventana de ejecución admin: {running_msg}")

        try:

            res_type, res_msg = admin_tool(
                self._db_session.get_real_connection()
            )

            msg_box.close()
            msg_box.deleteLater()

            if res_type == "error":
                QMessageBox.critical(self, "Resultado", res_msg)
            else:
                QMessageBox.information(self, "Resultado", res_msg)

        except Exception:
            msg_box.close()
            msg_box.deleteLater()

            QApplication.processEvents()
            raise
