import pandas as pd
import os
import re

from psycopg import OperationalError, DatabaseError
from psycopg.connection import Connection

from admin_tools.setup_database import is_database_ready
from auditing.audit import create_user
from core.sql_execution import execute_sql
from utils.logger import log
from utils.password_utils import generate_random_password

# ---------------------------
# CONSTANTES 
# ---------------------------

EXCEL_FILE = "imports/users_import.xlsx"

EXPECTED_COLUMNS = ['full_name', 'email']

# -----------------------------------------------
# FUNCIONALIDAD PRINCIPAL CREACIÓN DE USUARIOS 
# -----------------------------------------------

def create_users_from_excel(conn: Connection):

    flag = is_database_ready(conn)

    if not flag:
        msg = f"Es necesario ejecutar el setup inicial de la base de datos para crear usuarios."
        log(msg)
        return "error", msg

    try:
        check_file_exists()

        df = pd.read_excel(
            EXCEL_FILE,
            sheet_name = 'Users',
            engine = 'openpyxl'        
        )

        check_file_content(df)

        df = clean_df(df)

        df = generate_credentials(df)

        save_excel(df)

        #print(df_to_string(df))

        success, already_exists, errors = create_users_in_database(conn, df)

        log(
            f"Usuarios creados/actualizados con éxito: "
            f"{success}✅, {already_exists}👤, {errors}❌"
        )
        return "success", (
            f"Creación de usuarios finalizada:\n"
            f"- Nuevos: {success}\n"
            f"- Ya existentes: {already_exists}\n"
            f"- Errores: {errors}"
        )

    except PermissionError as e:
        log(f"No se puede abrir el archivo: {e}. Ciérralo si lo tienes abierto.", "error")
        return "error", f"No se puede abrir el archivo: {EXCEL_FILE}. Ciérralo si lo tienes abierto."
    except FileNotFoundError as e:
        log(f"Error al buscar el archivo: {e}", "error")
        return "error", f"Error al buscar el archivo {EXCEL_FILE}"
    except KeyError as e:
        log(f"Error con la estructura del archivo: {e}", "error")
        return "error", f"Error con la estructura del archivo: {EXCEL_FILE}"

# -----------------------------
# COMPROBACIONES DEL FICHERO
# -----------------------------

def check_file_exists():
    if not os.path.exists(EXCEL_FILE):
        raise FileNotFoundError(f"No se encontró el archivo: {EXCEL_FILE}")

def check_file_content(df):
    
    missing_columns = [
        col for col in EXPECTED_COLUMNS if col not in df.columns
    ]

    if missing_columns:
        raise KeyError(f"Faltan las columnas {missing_columns} en el archivo Excel: {EXCEL_FILE}")

# -----------------------------------------
# LIMPIEZA Y TRANSFORMACIÓN DE DATAFRAME
# -----------------------------------------

def clean_df(df):
    df = df.dropna(how='all')
    df = df.dropna(subset = EXPECTED_COLUMNS)
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    return df

def df_to_string(df):
    if df is None or df.empty:
        return "Dataframe vacío"

    output = []
    output.append(f"\n{'='*60}")
    output.append(f"Número de usuarios: {len(df)}")
    output.append(f"{'='*60}\n")

    for index, row in df.iterrows():
        output.append(f"Usuario #{index + 1}")
        output.append(f"  Nombre completo: {row['full_name']}")
        output.append(f"  Username:       {row['username']}")
        output.append(f"  Email:          {row['email']}")
        output.append("-" * 60)

    return "\n".join(output)

# -----------------------------
# GENERACIÓN DE CREDENCIALES 
# -----------------------------

def generate_credentials(df):
    if 'username' not in df.columns:
        df['username'] = ''
    if 'password' not in df.columns:
        df['password'] = ''

    generated_usernames = 0
    cleaned_usernames = 0
    generated_passwords = 0

    for index, row in df.iterrows():
       
        if pd.isna(row['username']) or str(row['username']).strip() == '':
            email = str(row['email'])
            if '@' in email:
                username_raw = email.split('@')[0]

                username_clean = clean_username(username_raw)

                df.at[index, 'username'] = username_clean
                generated_usernames += 1

        else:
            username_raw = str(row['username']).strip()

            username_clean = clean_username(username_raw)

            if username_raw != username_clean:
                df.at[index, 'username'] = username_clean
                cleaned_usernames += 1

        if pd.isna(row['password']) or str(row['password']).strip() == '':
            df.at[index, 'password'] = generate_random_password()
            generated_passwords += 1

    log(f"Usernames generados: {generated_usernames}")
    log(f"Usernames corregidos: {cleaned_usernames}")
    log(f"Passwords generadas: {generated_passwords}")

    return df

def clean_username(username: str):
    username_clean = re.sub(r'[^a-zA-Z0-9_]', '', username)

    if username_clean and not username_clean[0].isalpha():
        username_clean = 'user_' + username_clean

    username_clean = username_clean.lower()

    return username_clean

# -----------------------------------------------------------
# GUARDADO DE DATAFRAME Y CREACIÓN DE USUARIOS EN DATABASE
# -----------------------------------------------------------

def save_excel(df):
    try:
        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name='Users', index=False)
        log(f"Excel actualizado")

    except PermissionError as e:
        raise
    except Exception as e:
        log(f"Error al guardar los datos en Excel: {e}", "error")
        raise

def create_users_in_database(conn: Connection, df):
    
    success_count = 0
    already_exists_count = 0
    error_count = 0

    for index, row in df.iterrows():
        full_name = row['full_name']
        username = row['username']
        email = row['email']
        password = row['password']
        schema_name = f"schema_{username}"

        try:

            # Se crea rol para el usuario con su contraseña
            password_escaped = password.replace("'", "''")
            execute_sql(
                conn,
                f"CREATE ROLE {username} LOGIN PASSWORD '{password_escaped}';"
            )

            # Se añade al grupo de usuarios base
            execute_sql(
                conn,
                f"GRANT base_users TO {username};"
            )

            # Se crea el schema propio del usuario
            execute_sql(
                conn,
                f"CREATE SCHEMA IF NOT EXISTS {schema_name};"
            )

            # Se le revocan permisos a todos los usuarios base
            execute_sql(
                conn,
                f"REVOKE ALL ON SCHEMA {schema_name} FROM PUBLIC;"
            )
            execute_sql(
                conn,
                f"REVOKE ALL ON SCHEMA {schema_name} FROM base_users;"
            )

            # Se le dan permisos al usuario dueño del schema
            execute_sql(
                conn,
                f"GRANT USAGE, CREATE ON SCHEMA {schema_name} TO {username};"
            )

            # Se modifica el search path del usuario para que acceda 
            # directamente a su schema
            execute_sql(
                conn,
                f"ALTER ROLE {username} SET search_path = {schema_name};"
            )

            user_id = create_user(conn, full_name, username, email)
            log(f"Usuario creado: {user_id}, {username}, {schema_name}")
            success_count += 1

        except OperationalError:
            raise
            
        except DatabaseError as e:
            if type(e).__name__ == 'DuplicateObject':
                log(f"El usuario {username} para {full_name}, ya está creado")
                already_exists_count += 1
            else:
                log(f"Error creando usuario {username} para {full_name}", "error")
                error_count += 1
    
    return success_count, already_exists_count, error_count
