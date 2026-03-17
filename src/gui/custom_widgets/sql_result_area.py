
from PyQt6.QtWidgets import (
    QTabWidget
)

from gui.custom_widgets.sql_error_view import SQLErrorView
from gui.custom_widgets.sql_result_view import SQLResultView

class SQLResultArea(QTabWidget):

    def __init__(self):
        super().__init__()
        self._tabs_count = 0
        self._init_ui()
    
    def _init_ui(self):
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self._close_tab)

    def add_new_result_tab(self, columns, rows, row_count):
        result_panel = SQLResultView(
            columns = columns,
            rows = rows,
            row_count = row_count
        )
        self._tabs_count += 1
        title = f"Resultado {self._tabs_count}"
        index = self.addTab(result_panel, title)
        self.setCurrentIndex(index)

    def add_new_error_tab(self, error: Exception):
        error_panel = SQLErrorView(error)
        self._tabs_count += 1
        title = f"Resultado {self._tabs_count}"
        index = self.addTab(error_panel, title)
        self.setCurrentIndex(index)

    def _close_tab(self, index):
        self.removeTab(index)
