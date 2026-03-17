from PyQt6.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QWidget,
    QTableWidget,
    QTableWidgetItem
)

class SQLResultView(QWidget):

    def __init__(self, columns, rows, row_count):
        super().__init__()
        self._init_ui(columns, rows, row_count)

    def _init_ui(self, columns, rows, row_count):
        # Layout vertical
        layout = QVBoxLayout()

        # Tabla de resultados
        self._table = QTableWidget()
        if columns and rows:
            self._set_results(columns, rows)
            layout.addWidget(self._table)

        # Texto final
        self._text = QLabel(self._build_result_text(columns, rows, row_count))
        layout.addWidget(self._text)

        # Se establece el layout
        self.setLayout(layout)

    def _set_results(self, columns, rows):
        cols = [col.name for col in columns]
        self._table.setColumnCount(len(cols))
        self._table.setRowCount(len(rows))
        self._table.setHorizontalHeaderLabels(cols)

        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                self._table.setItem(row_idx, col_idx, item)

        self._table.resizeColumnsToContents()

    def _build_result_text(self, columns, row, row_count):
        if columns is not None and row is not None:
            return f"({row_count} filas)"
        
        if row_count is not None and row_count > -1:
            return f"OK ({row_count} filas afectadas)"

        return "OK"
