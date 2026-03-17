"""
Módulo que define funciones para cada operación de inserción o 
modificación en las tablas del sistema de auditoría.

Cada función recibe los datos a introducir en las tablas además de un
objeto de conexión de psycopg3.
"""

from psycopg import OperationalError, DatabaseError
from psycopg.connection import Connection

from core.sql_execution import execute_sql
from utils.error_handling import SqlAuditError

# ---------------------------
# QUERIES 
# ---------------------------

# Creación de usuario
Q_CREATE_USER = """
    SELECT auditing_functions.create_user(%s, %s, %s)
"""

# Obtener identificador de usuario a partir de su username
Q_GET_USER_ID_BY_USERNAME = """
    SELECT auditing_functions.get_user_id_by_username(%s)
"""

# Consultar si es necesario un cambio de contraseña
Q_NEEDS_PASSWORD_CHANGE = """
    SELECT auditing_functions.needs_password_change(%s)
"""

# Inicio de sesión
Q_START_SESSION = """
    SELECT auditing_functions.start_session(%s)
"""

# Cierre de sesión
Q_END_SESSION = """
    SELECT auditing_functions.end_session(%s)
"""

# Inicio de ejecución
Q_START_STATEMENT = """
    SELECT auditing_functions.start_statement(%s, %s, %s)
"""

# Fin de ejecución exitosa
Q_END_STATEMENT_OK = """
        SELECT auditing_functions.end_statement_ok(%s, %s)
    """

# Fin de ejecución fallida
Q_END_STATEMENT_ERROR = """
    SELECT auditing_functions.end_statement_error(%s)
"""

# Creación de error
Q_CREATE_ERROR = """
    SELECT auditing_functions.create_error(%s, %s, %s, %s)
"""

# ---------------------------------
# CAPA DE EJECUCIÓN DE AUDITORÍA
# ---------------------------------

def execute_audit_sql(
        conn: Connection, 
        query: str, 
        params: tuple, 
        audit_msg: str
    ):
    """
    Capa de ejecución de SQL para llamar a funciones de auditoría.
    Diferencia los errores de ejecución normales a los que se producen
    al registrar datos.
    """

    try:
        res = execute_sql(conn, query, params)['rows']

        # Validación centralizada:
        # Que exista resultado
        # Que tenga al menos una fila y una columna
        # Que el valor no sea None ni -1
        if not res or not res[0] or res[0][0] is None or res[0][0] == -1:
            raise SqlAuditError(f"Auditoría: {audit_msg}")
        
        return res[0][0]

    except OperationalError:
        raise
    except DatabaseError as e:
        msg = f"Auditoría: error de ejecución de SQL. {e}"
        raise SqlAuditError(msg)


# --------------------------- 
# FUNCIONES 
# ---------------------------

def create_user(
        conn: Connection,
        full_name: str,
        username: str,
        email: str
    ):
    """
    Creación de nuevo usuario en la tabla users.
    """
    
    params = (full_name, username, email)
    audit_msg = f"El usuario '{username}' no se ha registrado correctamente."
    return execute_audit_sql(conn, Q_CREATE_USER, params, audit_msg)
    
def get_user_id(
        conn: Connection,
        username: str
    ):
    """
    Obtener identificador de usuarios a partir de su nombre.
    """

    params = (username,)
    audit_msg = f"Usuario '{username}' no encontrado."
    return execute_audit_sql(conn, Q_GET_USER_ID_BY_USERNAME, params, audit_msg)

def needs_password_change(
        conn: Connection,
        username: str
    ):
    """
    Consultar si el usuario debe cambiar de contraseña.
    """

    params = (username,)
    audit_msg = f"No se puede comprobar si {username} debe cambiar de contraseña."
    return execute_audit_sql(conn, Q_NEEDS_PASSWORD_CHANGE, params, audit_msg)

def start_session(
        conn: Connection,
        username: str
    ):
    """
    Registrar inicio de sesión en auditoría.
    """

    user_id = get_user_id(conn, username)
    params = (user_id,)
    audit_msg = f"La sesión no se ha registrado correctamente."
    return execute_audit_sql(conn, Q_START_SESSION, params, audit_msg)

def end_session(
        conn: Connection,
        session_id: int
    ):
    """
    Registrar fin de sesión en auditoría.
    """

    params = (session_id,)
    audit_msg = f"No se ha registrado correctamente el fin de sesión."
    execute_audit_sql(conn, Q_END_SESSION, params, audit_msg)

def start_statement(
        conn: Connection,
        session_id: int,
        op_type: str,
        sql_text: str
    ):
    """
    Registrar inicio de ejecución en auditoría.
    """

    params = (session_id, op_type, sql_text)
    audit_msg = "La operación no se ha registrado correctamente."
    return execute_audit_sql(conn, Q_START_STATEMENT, params, audit_msg)

def end_statement_ok(
        conn: Connection,
        statement_id: int,
        row_count: int
    ):
    """
    Registrar fin de ejecución exitosa en auditoría.
    """

    params = (statement_id, row_count)
    audit_msg = f"No se ha registrado el fin de operación correctamente."
    execute_audit_sql(conn, Q_END_STATEMENT_OK, params, audit_msg)

def end_statement_error(
        conn: Connection,
        statement_id: int
    ):
    """
    Registrar fin de ejecución fallida en auditoría.
    """

    params = (statement_id,)
    audit_msg = f"No se ha registrado el fin de operación correctamente."
    execute_audit_sql(conn, Q_END_STATEMENT_ERROR, params, audit_msg)
    
def create_error(
        conn: Connection,
        statement_id: int,
        error_code: str,
        error_type: str,
        error_msg: str
    ):
    """
    Registrar error de ejecución en auditoría.
    """
    
    params = (statement_id, error_code, error_type, error_msg)
    audit_msg = f"El error no se ha registrado correctamente."
    return execute_audit_sql(conn, Q_CREATE_ERROR, params, audit_msg)
