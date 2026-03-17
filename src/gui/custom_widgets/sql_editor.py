from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPlainTextEdit
)
from PyQt6.QtGui import QFont
import sqlparse

class SQLEditor(QWidget):

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        # Layout vertical
        layout = QVBoxLayout()

        # Campo de escritura del editor
        self._editor = QPlainTextEdit()
        self._editor.setPlaceholderText("Escribe aquí tu SQL...")
        self._editor.setFont(QFont("Courier New", 11))
        self._editor.setMinimumHeight(150)

        layout.addWidget(self._editor)
        
        # Se establece el layout
        self.setLayout(layout)

    def get_sql(self):
        return self._editor.toPlainText()

    def get_current_sql(self):
        text = self._editor.toPlainText()
        pos = self._editor.textCursor().position()

        statements = sqlparse.split(text, strip_semicolon = False)

        offset = 0
        for stmt in statements:
            start = text.find(stmt, offset)

            if start == -1:
                continue

            end = start + len(stmt)

            if start <= pos <= end:
                return stmt.strip()

            offset = end

        return ""