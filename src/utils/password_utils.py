import string
import random

from psycopg import OperationalError, DatabaseError
from psycopg.connection import Connection

from core.sql_execution import execute_sql
from utils.error_handling import PasswordChangeError
from utils.logger import log

LOWERCASE = list(string.ascii_lowercase)
UPPERCASE = list(string.ascii_uppercase)
DIGITS = list(string.digits)
SPECIAL = list("!@#$%^&*()-_=+[]{}|;:,.<>?")

CHANGE_ROLE_PASSWORD = """
    SELECT aux_functions.change_role_password(%s, %s)
"""

def generate_random_password(length = 12):

    password = [
        random.choice(LOWERCASE),
        random.choice(UPPERCASE),
        random.choice(DIGITS),
        random.choice(SPECIAL)
    ]
    
    all_chars = LOWERCASE + UPPERCASE + DIGITS + SPECIAL
    password += random.choices(all_chars, k=length - 4)
    
    random.shuffle(password)
    
    return ''.join(password)

def is_valid_password(password: str):
    
    return (
        any(c in LOWERCASE for c in password) and
        any(c in UPPERCASE for c in password) and
        any(c in DIGITS for c in password) and
        any(c in SPECIAL for c in password) and
        len(password) >= 12
    )

def change_user_password(conn: Connection, user: str, password: str):
    params = (user, password)
    try:
        execute_sql(conn, CHANGE_ROLE_PASSWORD, params)

    except OperationalError:
        raise

    except DatabaseError:
        raise PasswordChangeError(f"No se pudo cambiar la contraseña de {user}.")
