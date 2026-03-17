from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem
)

from core.db_session import DatabaseSession
from core.schema_inspection import get_tables, get_views, get_functions
from utils.error_handling import handle_app_errors
from utils.logger import log

class DatabaseExplorer(QWidget):

    def __init__(self, db_session: DatabaseSession):
        super().__init__()
        self._db_session = db_session
        self._init_ui()

    def _init_ui(self):
        # Layout vertical general
        layout = QVBoxLayout()

        # Layout horizontal de la cabecera
        header_layout = QHBoxLayout()

        # Título
        self._title = QLabel("Base de datos: ")
        self._title.setStyleSheet("font-weight: bold; font-size: 13px;")
        
        header_layout.addWidget(self._title)
        header_layout.addStretch()

        # Se añade botón de actualización si es un usuario base
        if not self._db_session.is_admin():
            self._refresh_button = QPushButton("⟳")
            self._refresh_button.setFixedSize(24, 24)
            self._refresh_button.setToolTip("Refrescar")
            self._refresh_button.clicked.connect(self._refresh_and_expand)

            header_layout.addWidget(self._refresh_button)

        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)

        self.refresh()

        layout.addLayout(header_layout)

        layout.addWidget(self._tree)

        # Se establece layout
        self.setLayout(layout)

    def _refresh_and_expand(self):
        self.refresh()

        log(f"Expandiendo árbol.")

        self._tables_node.setExpanded(True)
        self._views_node.setExpanded(True)
        self._functions_node.setExpanded(True)

    @handle_app_errors
    def refresh(self):
        if self._db_session.is_admin():
            return

        log(f"Refrescando árbol...")

        self._tree.clear()

        self._tables_node = QTreeWidgetItem(self._tree, ["Tablas"])
        self._views_node = QTreeWidgetItem(self._tree, ["Vistas"])
        self._functions_node = QTreeWidgetItem(self._tree, ["Funciones"])

        self._load_tables(self._tables_node)
        self._load_views(self._views_node)
        self._load_functions(self._functions_node)
    
    def _load_tables(self, parent_node):
        tables = get_tables(self._db_session)

        for table_name, columns in tables.items():
            table_item = QTreeWidgetItem(parent_node, [table_name])

            for column, col_type in columns:
                QTreeWidgetItem(
                    table_item,
                    [f"{column} : {col_type}"]
                )

    def _load_views(self, parent_node):
        views = get_views(self._db_session)

        for view_name, columns in views.items():
            view_item = QTreeWidgetItem(parent_node, [view_name])

            for column, col_type in columns:
                QTreeWidgetItem(
                    view_item,
                    [f"{column} : {col_type}"]
                )

    def _load_functions(self, parent_node):
        functions = get_functions(self._db_session)

        for function_name in functions:
            QTreeWidgetItem(
                parent_node,
                [f"{function_name}()"]
            )
