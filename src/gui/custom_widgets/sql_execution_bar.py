from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton
)
from PyQt6.QtCore import pyqtSignal

class SQLExecutionBar(QWidget):

    run_clicked = pyqtSignal()
    run_all_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        # Layout horizontal
        layout = QHBoxLayout()

        # Botones de ejecución
        self._run_button = QPushButton("Run")
        self._run_all_button = QPushButton("Run All")

        self._run_button.clicked.connect(self.run_clicked.emit)
        self._run_all_button.clicked.connect(self.run_all_clicked.emit)

        layout.addWidget(self._run_button)
        layout.addWidget(self._run_all_button)

        # Empuja hacia la izquierda los elementos
        layout.addStretch()

        # Se establece el layout
        self.setLayout(layout)