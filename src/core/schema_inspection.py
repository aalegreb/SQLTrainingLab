"""
Módulo para la inspección de objetos creados en un schema de la base
de datos.
"""
from psycopg import OperationalError, DatabaseError

from core.sql_execution import execute_sql
from core.db_session import DatabaseSession
from utils.logger import log

# ---------------------------
#  QUERIES 
# ---------------------------

Q_GET_TABLES = """
    SELECT * FROM aux_functions.get_schema_tables(%s)
"""

Q_GET_VIEWS = """
    SELECT * FROM aux_functions.get_schema_views(%s)
"""

Q_GET_FUNCTIONS = """
    SELECT * FROM aux_functions.get_schema_functions(%s)
"""

# ---------------------------
# INSPECCIÓN DE SCHEMA
# ---------------------------

def execute_schema_query(db_session: DatabaseSession, query: str):
        """Ejecuta una consulta para inspeccionar el schema del usuario."""
        user_schema = f"schema_{db_session.get_username()}"
        params = (user_schema,)

        try:
            res = execute_sql(
                db_session.get_real_connection(),
                query,
                params
            )

            return res['rows']

        except OperationalError:
            raise

        except DatabaseError as e:
            log(f"Error consultando el schema del usuario.", "error")
            return []
        

def get_tables(db_session: DatabaseSession):
    rows = execute_schema_query(db_session, Q_GET_TABLES)

    tables = {}

    for table, column, col_type in rows:
        if table not in tables:
            tables[table] = []

        tables[table].append((column, col_type))

    return tables

def get_views(db_session: DatabaseSession):
    rows = execute_schema_query(db_session, Q_GET_VIEWS)

    views = {}

    for view, column, col_type in rows:
        if view not in views:
            views[view] = []

        views[view].append((column, col_type))

    return views

def get_functions(db_session: DatabaseSession):
    rows = execute_schema_query(db_session, Q_GET_FUNCTIONS)

    return [function_name for (function_name,) in rows]

