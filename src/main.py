
import sys

from config.settings import APP_CONFIG
from gui.gui_app_flow import main_gui
from terminal.terminal_app_flow import main_terminal
from utils.logger import log

def main():
    mode = APP_CONFIG["mode"].upper()

    if mode == "GUI":
        log(f"Iniciando SQLTrainingLab en modo GUI...")
        main_gui()
    elif mode == "TERMINAL":
        log(f"Iniciando SQLTrainingLab en modo TERMINAL...")
        main_terminal()
    else:
        log(f"El APP_MODE indicado en el archivo .env no es válido.", "error")
        sys.exit(1)

    
if __name__ == "__main__":
    main()