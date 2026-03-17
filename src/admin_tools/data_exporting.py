import pandas as pd
import os

from psycopg import OperationalError, DatabaseError
from psycopg.connection import Connection

from core.sql_execution import execute_sql
from utils.logger import log

# ---------------------------
# CONSTANTES 
# ---------------------------

SCHEMA_NAME = "auditing"

TABLES_TO_EXPORT = [
    ("users", "Users"),
    ("sessions", "Sessions"),
    ("statements", "Statements"),
    ("errors", "Errors")
]

CHECK_TABLE_EXISTS = """
    SELECT 1
    FROM information_schema.tables
    WHERE table_schema = %s
        AND table_name = %s
"""

EXCEL_FILE = "exports/auditing_data.xlsx"

# ------------------------------------------------------------
# FUNCIONALIDAD PRINCIPAL EXPORTACIÓN DE DATOS DE AUDITORÍA 
# ------------------------------------------------------------

def export_audit_data(conn: Connection):
    
    try:
        missing_tables = verify_tables(conn)

        if missing_tables:
            msg = f"No se pueden exportar los datos, faltan las tablas {missing_tables}"
            log(msg, "error")
            return "error", msg

        log(f"Se han encontrado todas las tablas de auditoría.")

        log(f"Iniciando exportación...")
        sheets_data = {}

        for table_name, sheet_name in TABLES_TO_EXPORT:
            full_table_name = f"{SCHEMA_NAME}.{table_name}"
            columns, rows = query_table_data(conn, full_table_name)

            if columns and rows is not None:
                sheets_data[sheet_name] = (columns, rows)
                log(f"{sheet_name}: {len(rows)} filas")
            else:
                log(f"{sheet_name}: sin datos", "warning")
                sheets_data[sheet_name] = (columns if columns else [], [])

        write_data_in_excel(sheets_data)
        
        msg = f"Datos exportados con éxito."
        log(msg)
        return "success", msg
    
    except PermissionError:
        msg = f"No se puede abrir el archivo {EXCEL_FILE}. Ciérralo si lo tienes abierto."
        log(msg, "error")
        return "error", msg

# ---------------------------
# VERFICACIÓN DE TABLAS
# ---------------------------

def verify_tables(conn: Connection):

    missing_tables = []

    for table_name, sheet_name in TABLES_TO_EXPORT:
        try:
            results = execute_sql(
                conn,
                CHECK_TABLE_EXISTS,
                (SCHEMA_NAME, table_name)
            )

            if not results['rows']:
                missing_tables.append(table_name)
                log(f"Tabla {table_name} no encontrada.")
            else:
                log(f"La tabla {table_name} se ha encontrado")

        except OperationalError:
            raise
            
        except DatabaseError:
            missing_tables.append(table_name)
            log(f"Tabla {table_name} no encontrada.")
    
    return missing_tables

# ---------------------------------
# CONSULTA DE DATOS DE AUDITORÍA 
# ---------------------------------

def query_table_data(conn: Connection, full_table_name: str):
    
    query = f"SELECT * FROM {full_table_name};"

    try:
        results = execute_sql(
            conn,
            query
        )

        columns = [col.name for col in results['columns']] if results['columns'] else []
        rows = results['rows'] if results['rows'] else []

        return columns, rows

    except OperationalError:
        raise
        
    except DatabaseError as e:
        log(f"Error consultando la tabla de auditoría {full_table_name}", "error")
        return None, None

# -----------------------------
# GUARDADO DE DATOS EN EXCEL 
# -----------------------------

def write_data_in_excel(sheets_data):

    os.makedirs(os.path.dirname(EXCEL_FILE), exist_ok = True)

    with pd.ExcelWriter(EXCEL_FILE, engine = 'openpyxl') as writer:
        for sheet_name, (columns, rows) in sheets_data.items():
            df = pd.DataFrame(rows, columns = columns)
            df.to_excel(writer, sheet_name = sheet_name, index = False)
    
    log(f"Archivo Excel guardado.")
