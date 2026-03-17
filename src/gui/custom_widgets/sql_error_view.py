from PyQt6.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QWidget,
    QPlainTextEdit
)
from PyQt6.QtGui import QFont

class SQLErrorView(QWidget):

    def __init__(self, error: Exception):
        super().__init__()
        self._init_ui(error)

    def _init_ui(self, error):
        # Layout vertical
        layout = QVBoxLayout()

        # Título
        self._title = QLabel("Error de ejecución:")
        self._title.setStyleSheet("font-weight: bold; color: #8b0000; font-size: 14px;")

        # Tipo de error
        self._error_type = QLabel(f"{type(error).__name__}")
        self._error_type.setStyleSheet("font-weight: bold;")

        # Mensaje de error
        self._message = QPlainTextEdit()
        self._message.setReadOnly(True)
        self._message.setPlainText(str(error))
        self._message.setFont(QFont("Courier New", 11))

        layout.addWidget(self._title)
        layout.addWidget(self._error_type)
        layout.addWidget(self._message)

        # Se establece el layout
        self.setLayout(layout)

