
from psycopg import OperationalError, DatabaseError
from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QSplitter,
    QMessageBox
)
from PyQt6.QtCore import Qt

from config.settings import APP_CONFIG
from core.db_session import DatabaseSession
from gui.custom_widgets.database_explorer import DatabaseExplorer
from gui.custom_widgets.sql_editor_area import SQLEditorArea
from gui.custom_widgets.sql_execution_bar import SQLExecutionBar
from gui.custom_widgets.sql_result_area import SQLResultArea
from utils.error_handling import handle_app_errors
from utils.sql_utils import get_all_statements_from_text

class MainWindow(QMainWindow):
    def __init__(self, db_session: DatabaseSession):
        super().__init__()
        self._db_session = db_session
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle(f" SQLTrainingLab v{APP_CONFIG['version']} | {self._db_session.get_username()}")
        self.setMinimumSize(900, 600)

        # Splitter para separar parte izquierda y derecha
        splitter = QSplitter(Qt.Orientation.Horizontal)

        ## Parte izquierda
        self._database_explorer = DatabaseExplorer(self._db_session)

        splitter.addWidget(self._database_explorer)
        ## Fin parte izquierda

        ## Parte derecha
        right_panel = QWidget()
        right_layout = QVBoxLayout()

        # Sección de pestañas de editores
        self._editor_area = SQLEditorArea()

        # Barra de botones de ejecución
        self._execution_bar = SQLExecutionBar()
        self._execution_bar.run_clicked.connect(self._run_sql)
        self._execution_bar.run_all_clicked.connect(self._run_all_sql)

        # Sección de pestañas de resultados
        self._result_area = SQLResultArea()
        
        right_layout.addWidget(self._editor_area)
        right_layout.addWidget(self._execution_bar)
        right_layout.addWidget(self._result_area)

        right_layout.setStretch(0, 3)
        right_layout.setStretch(1, 0)
        right_layout.setStretch(2, 2)
        
        right_panel.setLayout(right_layout)
        splitter.addWidget(right_panel)
        ## Fin parte derecha

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 4)

        self.setCentralWidget(splitter)

    # Ejecución SQL
    @handle_app_errors
    def _run_sql(self):
        editor = self._editor_area.get_current_editor()
        sql = editor.get_current_sql()
        if sql:
            self._execute_statements([sql])

    @handle_app_errors
    def _run_all_sql(self):
        editor = self._editor_area.get_current_editor()
        sql = editor.get_sql().strip()
        if sql:
            statements = get_all_statements_from_text(sql)
            self._execute_statements(statements)

    def _execute_statements(self, statements):
        if not statements:
            return

        for stmt in statements:
            try:
                results = self._db_session.process_user_sql(stmt)

                self._result_area.add_new_result_tab(
                    columns = results['columns'],
                    rows = results['rows'],
                    row_count = results['row_count']
                )

            except ValueError as e:
                QMessageBox.warning(
                    self,
                    "Error de validación",
                    str(e)
                )

            except OperationalError as e:
                raise
            
            except DatabaseError as e:
                self._result_area.add_new_error_tab(e)

        self._database_explorer.refresh()