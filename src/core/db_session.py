"""
Módulo que define la clase DatabaseSession, que implementa los mecanismos
necesarios para el correcto manejo de conexiones mediante psycopg3 como
una sesión de uso de la aplicación.
"""

import psycopg
from psycopg import OperationalError, DatabaseError

from auditing.audit import (
    start_session,
    end_session,
    start_statement,
    end_statement_ok,
    end_statement_error,
    create_error
)
from config.settings import DB_CONFIG, SQL_CONFIG
from utils.logger import log
from utils.sql_utils import (
    validate_user_sql,
    classify_statement,
    clean_comments
)
from core.sql_execution import execute_sql

class DatabaseSession:
    """
    Clase que representa una sesión de uso de SQLTrainingLab o una conexión a
    PostgreSQL a través de la aplicación. Añade a la conexión con la base
    de datos y a la ejecución de SQL la capa de auditoría necesaria para
    registrar la actividad realizada.

    Proporciona la funcionalidad para conectar, desconectar, procesar
    SQL, obtener el objeto de conexión real de psycopg, hacer commits, 
    hacer rollbacks.
    """

    def __init__(self, user: str, password: str):
        self._user = user # Nombre del usuario dueño de la conexión
        self._password = password # Contraseña de acceso
        self._conn = None # Objeto de conexión a PostgreSQL
        self._session_id = None # Identificador de sesión actual (auditoría)

        # Determina si el usuario conectado es administrador
        self._is_admin = (user == DB_CONFIG["admin_user"])

    # -------------------------------
    # Soporte para context manager
    # -------------------------------

    def __enter__(self):
        """
        Soporte para inicio de context manager: establece la conexión.
        """
        self.connect()
        return self

    def __exit__(self, eType, eValue, eTraceback):
        """
        Soporte para salida de context manager : limpia recursos al 
        salir.
        
        Revierte la transacción actual en caso de error, y la confirma 
        en caso de que se finalice de manera voluntaria.
        """

        if eType:
            self.rollback()
            log(
                f"Transacción revertida en fin de conexión "
                f"{self._user} -> {eValue}"
            )
        else:
            self.commit()
            log(f"Transacción confirmada en fin de conexión {self._user}")
        self.disconnect()

    # ---------------------------
    # Métodos de ciclo de vida
    # ---------------------------

    def connect(self):
        """Método para iniciar la conexión con la base de datos."""

        # Se crea y almacena la nueva conexión
        self._conn = psycopg.connect(
            dbname = DB_CONFIG["dbname"],
            user = self._user,
            password = self._password,
            host = DB_CONFIG["host"],
            port = DB_CONFIG["port"],
            sslmode = DB_CONFIG["ssl_mode"],
            connect_timeout = DB_CONFIG["connect_timeout"]
        )

        # Por seguridad, deja de almacenarse la contraseña en memoria
        self._password = None

        # Sentencias SQL para la configuración de timeouts
        timeout_sql_statements = [
            f"SET statement_timeout = {SQL_CONFIG['statement_timeout']}",
            f"SET idle_in_transaction_session_timeout = "
            f"{SQL_CONFIG['idle_in_transaction_session_timeout']}"
        ]

        for stmt in timeout_sql_statements:
            # No se capturan errores de sql, si falla esto, debe 
            # cerrarse el programa
            execute_sql(self._conn, stmt)

        # Si no es administrador, se registra inicio de sesión
        if not self._is_admin:
            self._session_id = start_session(self._conn, self._user)
            log(
                f"Conectado con auditoría a la base de datos como "
                f"{self._user}"
            )
        else:
            log(
                f"Conectado sin auditoría a la base de datos como "
                f"{self._user}"
            )

    def disconnect(self):
        """Cierra la conexión si esta existe y sigue abierta."""
        
        if self._conn and self.is_alive():
            # Si no es administrador, se registra fin de sesión
            if not self._is_admin:
                end_session(self._conn, self._session_id)
                log(f"Sesión de auditoría finalizada.")

            self._conn.close()
            log(f"Conexión finalizada.")

    # ------------------------
    # Control transaccional
    # ------------------------

    def commit(self):
        """Confirma la transacción actual."""
        self._conn.commit()
        log(f"Commit realizado.")

    def rollback(self):
        """Revierte la transacción actual."""
        self._conn.rollback()
        log(f"Rollback realizado.")

    # ------------------------
    # Ejecución de SQL
    # ------------------------

    def process_user_sql(self, statement: str):
        """
        Ejecuta una sentencia SQL introducida por el usuario.
        En caso de ser administrador, la ejecuta de manera cruda.
        En caso de no serlo, se añade el registro de datos de actividad
        con llamadas a auditoría.
        """

        clean_stmt = clean_comments(statement)

        if self._is_admin:
            return execute_sql(self._conn, clean_stmt)
        
        # Validación de la sentencia
        valid, reason, fw = validate_user_sql(clean_stmt)
        if not valid:
            if reason == "length":
                msg = f"La query {clean_stmt} es demasiado larga."
                log(msg)
                raise ValueError(msg)
            else:
                msg = f"La query {clean_stmt} contiene palabra/s prohibida/s: {fw}"
                log(msg)
                raise ValueError(msg)
        
        # Registro de inicio de ejecución
        statement_id = None
        if self._session_id:
            statement_id = start_statement(
                self._conn,
                self._session_id,
                classify_statement(clean_stmt),
                clean_stmt
            )

        # Ejecución de la sentencia
        try:
            results = execute_sql(self._conn, clean_stmt)

            # Si se ha registrado bien el inicio de ejecución se 
            # registra el fin
            if statement_id:
                # Fin exitoso
                end_statement_ok(
                    self._conn,
                    statement_id,
                    results['row_count']
                )

            return results
        
        except OperationalError:
            raise

        except DatabaseError as e:
            # Si se ha registrado bien el inicio de ejecución se 
            # registra el fin
            if statement_id:
                # Fin con error
                end_statement_error(
                    self._conn,
                    statement_id
                )

                # Registro de error
                error_id = create_error(
                    self._conn,
                    statement_id,
                    str(getattr(e, 'sqlstate', None)),
                    type(e).__name__,
                    str(e).strip()
                )

            raise

    # ------------------------
    # Métodos de estado
    # ------------------------

    def is_alive(self):
        """Retorna si la conexión sigue activa."""
        return not (self._conn.closed or self._conn.broken)

    def is_admin(self):
        """
        Retorna si la sesión pertenece al administrador
        """
        return self._is_admin
    
    # ----------
    # Getters
    # ----------

    def get_real_connection(self):
        """
        Retorna el objeto de la conexión real de psycopg3
        """
        return self._conn

    def get_username(self):        
        return self._user
    
