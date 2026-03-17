
from PyQt6.QtWidgets import (
    QTabWidget,
    QPushButton
)
from PyQt6.QtCore import Qt

from gui.custom_widgets.sql_editor import SQLEditor

class SQLEditorArea(QTabWidget):
    
    def __init__(self):
        super().__init__()
        self._editors_count = 0
        self._init_ui()

    def _init_ui(self):
        self.setCornerWidget(
            self._create_add_tab_button(),
            Qt.Corner.TopRightCorner
        )
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self._close_tab)
        self._add_new_editor_tab()
    
    def _create_add_tab_button(self):
        button = QPushButton("+")
        button.setFixedSize(24, 24)
        button.clicked.connect(self._add_new_editor_tab)
        return button

    def _add_new_editor_tab(self):
        new_editor = SQLEditor()
        self._editors_count += 1
        index = self.addTab(new_editor, f"Editor {self._editors_count}")
        self.setCurrentIndex(index)

    def _close_tab(self, index):
        if self.count() > 1:
            self.removeTab(index)

    def get_current_editor(self):
        return self.currentWidget()
       