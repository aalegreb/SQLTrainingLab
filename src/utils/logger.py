import logging
import os
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILENAME = os.path.join(LOG_DIR, f"{datetime.now().strftime('%Y-%m-%d')}.log")

logging.basicConfig(
    level = logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILENAME, encoding='utf-8')#,
        #logging.StreamHandler() # Comentar esta línea para dejar de mostrar en consola
    ]
)

def log(message: str, kind: str = "info"):

    logger = logging.getLogger()

    if kind == "error":
        logger.error(message)
    elif kind == "warning":
        logger.warning(message)
    else:
        logger.info(message)