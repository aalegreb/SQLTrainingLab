import re

from sqlparse import parse

from config.settings import SQL_CONFIG

FORBIDDEN_KEYWORDS = [
    "INFORMATION_SCHEMA", "ROLE", "DATABASE",
    "GRANT", "REVOKE", "AUTHORIZATION", "SEARCH_PATH",
    "PRIVILEGES", "AUDITING", "AUDITING_FUNCTIONS", "AUX_FUNCTIONS"]

OP_TYPES = ["SELECT", "INSERT", "UPDATE",
                "DELETE", "TRUNCATE", "CREATE", 
                "ALTER", "DROP"]

def get_all_statements_from_text(sql_text: str):
    statements = parse(sql_text)
    return [str(stmt).strip() for stmt in statements if str(stmt).strip()]

def validate_user_sql(sql_text: str):
    if not validate_statement_length(sql_text):
        return False, "length", None

    valid_content, forbidden_word = validate_statement_content(sql_text)
    if not valid_content:
        return False, "forbidden_word", forbidden_word
    
    return True, None, None

def validate_statement_length(sql_text: str):
    return len(sql_text) <= SQL_CONFIG["max_statement_length"]

def validate_statement_content(sql_text: str):

    tokens = set(re.findall(r"\b\w+\b", sql_text.upper()))

    for token in tokens:
        if token.startswith("PG_") or token in FORBIDDEN_KEYWORDS:
            return False, token

    return True, None

def clean_comments(sql_content: str):
    # Secciones de comentarios
    sql_no_comments = re.sub(r"/\*.*?\*/", "", sql_content, flags=re.DOTALL)

    # Comentarios de una línea
    sql_no_comments = re.sub(r"--.*?$", "", sql_no_comments, flags=re.MULTILINE)
    
    return sql_no_comments

def classify_statement(sql_text: str):
    
    first_word = sql_text.strip().upper().split()[0]
    if first_word in OP_TYPES:
        return first_word
    else:
        if first_word == "WITH":
            return "SELECT"
        return "OTHER"