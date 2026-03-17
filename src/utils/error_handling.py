from functools import wraps
from psycopg import OperationalError
from PyQt6.QtWidgets import QApplication

from utils.logger import log

class SqlAuditError(Exception):
    pass

class PasswordChangeError(Exception):
    pass

def handle_app_errors(func):
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except OperationalError as e:
            app = QApplication.instance()
            if hasattr(app, "handle_operational_error"):
                error_msg = str(e)
                log(error_msg, "error")
                msg = classify_operational_error(error_msg)

                app.handle_operational_error(msg)

        except SqlAuditError as e:
            app = QApplication.instance()

            if hasattr(app, "handle_fatal_error"):
                log(f"{str(e)}", "error")
                app.handle_fatal_error("Se ha producido un error en el sistema de auditoría.")

        except PasswordChangeError as e:
            app = QApplication.instance()

            if hasattr(app, "handle_fatal_error"):
                log(f"{str(e)}", "error")
                app.handle_fatal_error("Se ha producido un error al cambiar la contraseña")

        except Exception as e:
            app = QApplication.instance()

            if hasattr(app, "handle_fatal_error"):
                log(f"Error fatal: {str(e)}", "error")
                app.handle_fatal_error("Se ha producido un error fatal inesperado.")
 
    return wrapper

def classify_operational_error(error_msg: str):
    if "authentication failed" in error_msg:
        return "Credenciales incorrectas, inténtalo de nuevo."
    elif "does not exist" in error_msg:
        return "La base de datos a la que se quiere conectar no existe."
    elif "could not connect" in error_msg or "Connection refused" in error_msg:
        return "No se pudo conectar al servidor. Verifica el host y el puerto de conexión."
    elif "is lost" in error_msg:
        return "La conexión se ha perdido."
    elif "timeout expired" in error_msg:
        return "No se ha podido establecer conexión dentro del tiempo límite."
    elif "statement timeout" in error_msg:
        return "Se ha alcanzado el tiempo límite de ejecución."
    else:
        return "Error intentando conectar."