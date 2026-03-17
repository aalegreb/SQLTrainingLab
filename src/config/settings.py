from dotenv import load_dotenv
import os

load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "ssl_mode": os.getenv("DB_SSL_MODE"),
    "connect_timeout": 5,
    "admin_user": os.getenv("ADMIN_USER")
}

SQL_CONFIG = {
    "statement_timeout": 30000,
    "idle_in_transaction_session_timeout": 600000,
    "max_statement_length": 10000
}

APP_CONFIG = {
    "version": "1.0",
    "mode": os.getenv("APP_MODE")
}