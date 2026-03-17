"""
Módulo que implementa la ejecución cruda de sentencias SQL individuales
y desde fichero .sql.
"""

from psycopg import OperationalError, DatabaseError
from psycopg.connection import Connection

from utils.logger import log
from utils.sql_utils import get_all_statements_from_text, clean_comments

def execute_sql(conn: Connection, query: str, params=None):
    """
    Función de ejecución general de SQL.

    :param conn: Conexión activa a la base de datos
    :param query: Sentencia SQL a ejecutar
    :param params: Parámetros opcionales para inyectar en la sentencia
    :return: Diccionario con:
            - columns: metadatos de columna (si aplica)
            - rows: datos de las filas obtenidas (si aplica)
            - row_count: número de filas afectadas u obtenidas
    :raises OperationalError: Se eleva cualquier error de conexión producido
    :raises DatabaseError: Si ocurren errores de ejecución
    """
    
    try:
        # Context manager para liberar automáticamente recursos de 
        # ejecución
        with conn.cursor() as cur:

            cur.execute(query, params)
            
            # Metadatos de columnas (None si no retorna filas)
            columns = cur.description

            # Recupera resultados si la ejecución produce filas
            rows = cur.fetchall() if columns else None

            # Número de filas afectadas u obtenidas
            row_count = cur.rowcount

        # Se confirma transacción siempre que no haya errores
        conn.commit()

        # Se retorna un diccionario con cada parte de los resultados
        return {
            'columns': columns,
            'rows': rows,
            'row_count': row_count
        }

    except OperationalError:
        raise

    except DatabaseError as e:
        log(
            f"Error ejecutando SQL: "
            f"{type(e).__name__} | "
            f"{getattr(e, 'sqlstate', None)} | "
            f"{e}",
            "error"
        )

        # En caso de error, se revierte la transacción
        conn.rollback()

        raise

def execute_script_sql(conn: Connection, sql_file_path: str):
    """
    Función de ejecución de archivos .sql completos.

    :param conn: Conexión activa a la base de datos.
    :param sql_file_path: Ruta al archivo SQL a ejecutar.
    """

    log(f"Cargando archivo SQL: {sql_file_path}")

    # Se abre y lee el archivo
    with open(sql_file_path, "r", encoding = "utf-8") as f:
        sql_content = f.read()

    # Se extraen todas las sentencias del archivo
    statements = get_all_statements_from_text(sql_content)
    log(f"Total de sentencias SQL encontradas: {len(statements)}")

    # Se ejecuta cada sentencia
    for i, stmt in enumerate(statements, start = 1):
        clean_stmt = clean_comments(stmt)
        if not clean_stmt:
            continue

        log(f"Ejecutando sentencia {i}...")
        try:
            # Se ejecutan de manera interna
            execute_sql(conn, clean_stmt)
        
        except OperationalError:
            raise
        
        except DatabaseError as e:
            log(
                f"Error ejecutando archivo {sql_file_path}, "
                f"sentencia {clean_stmt}: \n{str(e)}",
                "error"
            )

    log(f"Fin de ejecución del archivo {sql_file_path}.")
