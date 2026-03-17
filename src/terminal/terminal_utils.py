# Librerías estándar
import os
import time
import getpass

from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings

from config.settings import APP_CONFIG
from utils.password_utils import SPECIAL, is_valid_password

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_banner(user: str):
    clear_screen()
    print("="*104)
    print(f" SQLTrainingLab v{APP_CONFIG['version']} | Sesión iniciada como {user} ")
    print(f" Enter para saltos de línea, Ctrl+J para confirmar entrada ")
    print("="*104, "\n")
    time.sleep(0.3)

def show_admin_banner():
    clear_screen()
    print("="*104)
    print(f" SQLTrainingLab v{APP_CONFIG['version']} ")
    print(f" Sesión iniciada como administrador | Seleccione lo que desea hacer ")
    print("="*104, "\n")
    time.sleep(0.3)

def show_custom_banner(text: str):
    clear_screen()
    print("="*104)
    print(f" SQLTrainingLab v{APP_CONFIG['version']} \n ~{text}~")
    print("="*104, "\n")
    time.sleep(0.3)

def show_exit():
    print("\nCerrando sesión...")
    time.sleep(0.8)
    clear_screen()
    print("👋 Sesión finalizada. Hasta pronto.\n")

def show_error_exit():
    print("\nLa aplicación se cerrará.")
    time.sleep(1.5)
    clear_screen()
    print("👋 Hasta pronto.\n")

def get_credentials():
    print(f"\n==========Introduce usuario y contraseña==========\n")
    user = input("Usuario: ")
    password =  getpass.getpass("Contraseña: ")#input("Contraseña: ")
    return user, password

def get_new_password():
    print(f"La contraseña debe ser de al menos 12 caracteres y contener al",
          f"menos una mayúscula, una minúscula, un dígito y uno de los",
          f"siguientes caracteres:\n{SPECIAL}\n")
    while True:
        
        new_password = getpass.getpass("Nueva contraseña: ") #input("Introduce una nueva contraseña: ")
        confirm_password = getpass.getpass("Confirma contraseña: ") #input("Confirma la contraseña: ")

        if new_password != confirm_password:
            print("Las contraseñas no coinciden.\n")
            continue

        if not is_valid_password(new_password):
            print("La contraseña no cumple los requisitos mencionados.\n")
            continue

        break

    return new_password

def show_admin_options():
    show_admin_banner()
    print(f"1. Setup inicial de la base de datos")
    print(f"2. Crear usuarios a partir de Excel")
    print(f"3. Exportar datos de auditoría")
    print(f"4. Acceder a la app")
    print(f"5. Salir")

    return input("\nOpción--> ")

# ------------------------------------------
# MUESTRA DE RESULTADOS SQL
# ------------------------------------------

def rows_to_dict(columns, rows):

    column_names = [col.name for col in columns]
    return [dict(zip(column_names, row)) for row in rows]

def print_table(dict_rows):
    if not dict_rows:
        print("\n(0 filas)\n")
        return
    
    cols = list(dict_rows[0].keys())
    col_widths = {
        col: max(len(col), max(len(str(row[col])) for row in dict_rows)) for col in cols
    }

    sep = "+-" + "-+-".join("-" * col_widths[col] for col in cols) + "-+"
    header = "| " + " | ".join(col.ljust(col_widths[col]) for col in cols) + " |"

    print()
    print(sep)
    print(header)
    print(sep)

    for row in dict_rows:
        line = "| " + " | ".join(str(row[col]).ljust(col_widths[col]) for col in cols) + " |"
        print(line)

    print(sep)
    print(f"({len(dict_rows)} filas)\n")

def show_results(rows = None, columns = None, row_count: int = None):

    if rows is not None and columns is not None:
        dict_rows = rows_to_dict(columns, rows)
        print_table(dict_rows)
    else:
        if row_count is not None and row_count > -1:
            print(f"\nOK ({row_count} filas afectadas)\n")
        else:
            # CREATE, ALTER y DROP devuelven -1 filas
            print("\nOK\n")

# ------------------------------------------
# LECTURA MULTILÍNEA
# ------------------------------------------

kb = KeyBindings()

@kb.add('c-j')
def _(event):
    event.app.exit(result=event.app.current_buffer.text)

@kb.add('enter')
def _(event):
    buffer = event.app.current_buffer
    buffer.insert_text("\n")

session = PromptSession(multiline=True, key_bindings=kb)

def read_sql(user: str) -> str:
    raw = session.prompt(f"[SQLTrainingLab] {user}>> ")

    lines = [line for line in raw.splitlines() if not line.lstrip().startswith("--")]
    cleaned_sql = "\n".join(lines).strip()

    return cleaned_sql