from psycopg import OperationalError, DatabaseError
from psycopg.connection import Connection

from core.sql_execution import execute_sql, execute_script_sql
from utils.logger import log

# ---------------------------
# SCRIPTS SQL 
# ---------------------------

FILES = [
    "sql/setup_database.sql", 
    "sql/auditing_tables.sql",
    "sql/auditing_functions.sql",
    "sql/aux_functions.sql"
]

# ---------------------------
# SCHEMAS 
# ---------------------------

AUDIT_SCHEMA = "auditing"
AUDITING_FUNCTIONS_SCHEMA = "auditing_functions"
AUX_FUNCTIONS_SCHEMA = "aux_functions"

# ---------------------------
# TABLAS Y FUNCIONES 
# ---------------------------

AUDIT_TABLES = [
    "users",
    "sessions",
    "statements",
    "errors"
]

AUDITING_FUNCTIONS = [
    "create_user",
    "get_user_id_by_username",
    "needs_password_change",
    "start_session",
    "end_session",
    "start_statement",
    "end_statement_ok",
    "end_statement_error",
    "create_error"
] 

AUX_FUNCTIONS = [
    "change_role_password",
    "get_schema_tables",
    "get_schema_views",
    "get_schema_functions"
]

# ---------------------------
# CONSULTAS SQL 
# ---------------------------

CHECK_TABLE_EXISTS = """
    SELECT 1
    FROM information_schema.tables
    WHERE table_schema = %s
        AND table_name = %s
"""

CHECK_FUNCTION_EXISTS = """
    SELECT 1
    FROM pg_proc p
    JOIN pg_namespace n ON p.pronamespace = n.oid
    WHERE n.nspname = %s
        AND p.proname = %s
"""

# --------------------------------
# FUNCIONALIDAD PRINCIPAL SETUP 
# --------------------------------

def setup_database(conn: Connection):

    log(f"Comprobando si ya se ejecutó Setup...")

    flag = is_database_ready(conn)

    log(f"Instancia lista: {flag}")

    if flag:
        msg = f"No es necesario ejecutar Setup, la base de datos ya está configurada."
        log(msg)
        return "error", msg

    log(f"Iniciando setup de la instancia de PostgreSQL...")

    for f in FILES:
        log(f"Ejecutando archivo de setup {f}...")
        execute_script_sql(conn, f)
        log(f"Archivo de setup {f} ejecutado con éxito.")

    msg = f"Finalizado proceso de Setup."
    log(msg)
    return "success", msg

def is_database_ready(conn: Connection):
    
    try:
        for table in AUDIT_TABLES:
            results = execute_sql(
                conn,
                CHECK_TABLE_EXISTS,
                (AUDIT_SCHEMA, table)
            )

            if len(results['rows']) == 0:
                return False

        for func in AUDITING_FUNCTIONS:
            results = execute_sql(
                conn,
                CHECK_FUNCTION_EXISTS,
                (AUDITING_FUNCTIONS_SCHEMA, func)
            )

            if not results['rows']:
                return False

        for func in AUX_FUNCTIONS:
            results = execute_sql(
                conn,
                CHECK_FUNCTION_EXISTS,
                (AUX_FUNCTIONS_SCHEMA, func)
            )

            if not results['rows']:
                return False

        return True

    except OperationalError:
        raise
        
    except DatabaseError:
        return False
