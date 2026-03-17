import sys

from PyQt6.QtWidgets import QApplication, QMessageBox

from auditing.audit import needs_password_change
from core.db_session import DatabaseSession
from gui.admin_tools_window import AdminToolsWindow
from gui.change_password_window import ChangePasswordWindow
from gui.login_window import LoginWindow
from gui.main_window import MainWindow
from utils.error_handling import handle_app_errors
from utils.logger import log

class App(QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        self._login_window = None
        self._change_password_window = None
        self._admin_tools_window = None
        self._main_window = None
        self._db_session = None

        self.aboutToQuit.connect(self._on_app_exit)

    # ----------------------------------
    # Flujo de la app
    # ----------------------------------

    def start(self):
        print("Iniciando app...")
        self._login_window = LoginWindow()
        self._login_window.login_requested.connect(self._attempt_login)
        self._login_window.show()
        sys.exit(self.exec())

    @handle_app_errors
    def _attempt_login(self, user, password):
        self._db_session = DatabaseSession(user, password)
        self._db_session.connect()

        log("GUI: conexión exitosa, abriendo main window...")

        if self._db_session.is_admin():
            self._admin_tools_window = AdminToolsWindow(self._db_session)
            self._admin_tools_window.show()
            self._admin_tools_window.enter_app_clicked.connect(
                self._create_and_show_main
            )
        else:
            if needs_password_change(
                self._db_session.get_real_connection(),
                self._db_session.get_username()
            ):
                self._change_password_window = ChangePasswordWindow(
                    self._db_session
                )
                self._change_password_window.password_changed.connect(
                    self._create_and_show_main
                )
                self._change_password_window.show()
            else:
                self._create_and_show_main()

        self._login_window.hide()

    def _create_and_show_main(self):
        self._main_window = MainWindow(self._db_session)
        self._main_window.show()

        self._close_secondary_windows()

    def _on_app_exit(self):
        if self._db_session and self._db_session.is_alive():
            log(f"Desconectando de la base de datos por cierre de la GUI.")
            print("Cerrando app...")
            self._db_session.disconnect()

    # ----------------------------------
    # Manejo de errores
    # ----------------------------------

    def handle_operational_error(self, msg):
        if self._main_window:
            self._main_window.close()
            self._main_window = None

        self._close_secondary_windows()

        if self._login_window and not self._login_window.isVisible():
            self._login_window.show()

        QMessageBox.critical(self._login_window, "Error", msg)
        self._login_window.clear_password_field()

    def handle_fatal_error(self, msg):
        active_widget = (
            self._main_window
            or self._change_password_window
            or self._admin_tools_window
            or self._login_window
        )

        QMessageBox.critical(active_widget, "Error", msg)

        log("App cerrada tras producirse un error fatal.", "error")

        self.exit(1)        
        
    # ----------------------------------
    # Cierre de ventanas secundarias
    # ----------------------------------
    
    def _close_secondary_windows(self):
        if self._admin_tools_window:
            self._admin_tools_window.close()
            self._admin_tools_window = None

        if self._change_password_window:
            self._change_password_window.close()
            self._change_password_window = None

# -----------------------------
# Ejecución principal de GUI 
# -----------------------------

def main_gui():
    app = App()
    app.start()