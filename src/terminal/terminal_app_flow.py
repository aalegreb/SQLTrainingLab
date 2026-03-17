import time

from psycopg import OperationalError, DatabaseError

from core.db_session import DatabaseSession
from utils.error_handling import (
    SqlAuditError,
    PasswordChangeError,
    classify_operational_error
)
from utils.sql_utils import get_all_statements_from_text
from utils.logger import log
from admin_tools.setup_database import setup_database
from admin_tools.data_exporting import export_audit_data
from admin_tools.user_creation import create_users_from_excel
from auditing.audit import needs_password_change
from terminal.terminal_utils import (
    read_sql,
    show_banner,
    show_custom_banner,
    show_admin_options,
    show_exit,
    show_error_exit,
    get_new_password,
    get_credentials,
    show_results
)
from utils.password_utils import change_user_password

# ------------------------------------------
# COMPROBACIÓN Y GESTIÓN DEL PRIMER LOGIN 
# ------------------------------------------

def check_and_handle_first_login(db_session: DatabaseSession):
    if not needs_password_change(
        db_session.get_real_connection(), 
        db_session.get_username()
    ):
        return

    print("Es necesario cambiar la contraseña\n")
    
    new_password = get_new_password()

    change_user_password(
        db_session.get_real_connection(),
        db_session.get_username(),
        new_password
    )
  
# ---------------------------------
# EDITOR INTERACTIVO DE TERMINAL 
# ---------------------------------

def handle_input(db_session: DatabaseSession):
    user = db_session.get_username()
    show_banner(user)
    while True:
        #query = input(f"[SQLTrainingLab] {user}>> ").strip()
        sql_text = read_sql(user)

        if not sql_text:
            continue

        if sql_text.lower() in ['exit', 'quit']:
            break

        if sql_text.lower() == "clear":
            show_banner(user)
            continue

        statements = get_all_statements_from_text(sql_text)
        
        print()
        for i in range(len(statements)):
            print("="*25)
            print(f"=  Operación {i+1}          =")
            print("="*25)
            
            try:
                results = db_session.process_user_sql(statements[i])

                show_results(
                    results['rows'],
                    results['columns'],
                    results['row_count']
                )   

            except ValueError as e:
                print(f"❌ {e}")

            except OperationalError as e:
                raise
            
            except DatabaseError as e:
                print(f"\n❌ Error sql: "
                      f"{type(e).__name__} | "
                      f" Código: {getattr(e, 'sqlstate', None)}"
                      f"\n{e}")
        
            print()

    print(f"\nCerrando app...")

# --------------------------------
# HERRAMIENTAS DE ADMINISTRADOR 
# --------------------------------

def handle_admin_options(db_session: DatabaseSession):
    while True:
        option = show_admin_options()

        if option == "1":
            show_custom_banner("SETUP DE LA BASE DE DATOS")
            res_type, res_msg = setup_database(db_session.get_real_connection())

        elif option == "2":
            show_custom_banner("CREACIÓN DE USUARIOS")
            res_type, res_msg = create_users_from_excel(db_session.get_real_connection())

        elif option == "3":
            show_custom_banner("EXPORTACIÓN DE DATOS DE AUDITORÍA")
            res_type, res_msg = export_audit_data(db_session.get_real_connection())

        elif option == "4":
            handle_input(db_session)
            continue

        elif option == "5":
            break

        else:
            continue

        if res_type and res_msg and isinstance(res_type, str) and isinstance(res_msg, str):
            res_icon = "❌" if res_type == "error" else "✅"
            print(res_icon, res_msg)

        time.sleep(3)

# ----------------------------------
# EJECUCIÓN PRINCIPAL DE TERMINAL 
# ----------------------------------

def main_terminal():
    try:
        while True:
            user, password = get_credentials()
            print()

            try:
                with DatabaseSession(user, password) as db_session:

                    if db_session.is_admin():
                        handle_admin_options(db_session)
                    else:
                        check_and_handle_first_login(db_session)
                        handle_input(db_session)

                show_exit()
                break
                
            except OperationalError as e:
                error_msg = str(e)
                log(error_msg, "error")

                msg = classify_operational_error(error_msg)
                print(f"❌ {msg}")

            except SqlAuditError as e:
                log(f"{str(e)}", "error")
                print("❌ Se ha producido un error en el sistema de auditoría.")

            except PasswordChangeError as e:
                log(f"{str(e)}", "error")
                print(f"❌ Se ha producido un error al cambiar la contraseña")
            
            except Exception as e:
                log(f"Error fatal: {e}", "error")
                print("❌ Se ha producido un error fatal inesperado.")

            retry = input("\n¿Quieres reintentar la conexión? (s/n) --> ")

            if retry.lower() != "s":
                show_error_exit()
                break 

    except KeyboardInterrupt:
        msg = f"Aplicación finalizada forzosamente por el usuario."
        log(msg)
        print("\n", msg)

        show_error_exit()