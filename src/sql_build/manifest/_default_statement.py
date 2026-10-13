import logging

from .logging_config import app_name


def _create_statement(statement_words:list[str], sql_words:list[str]):
    found = [w for w in statement_words if w in sql_words]
    statement = ""
    if len(found) == len(statement_words):
        statement = " ".join(statement_words)
    return statement

_STATEMENT_KEY = "statement_identifier"

def default_statement(sql:str, statements:list[dict]):
    try:
        if not statements:
            return statements
        if not _STATEMENT_KEY in statements[0]:
            return statements
        if statements[0][_STATEMENT_KEY]:
            return statements
    except (ValueError, TypeError, KeyError):
        return statements

    log = logging.getLogger(app_name)
    log.warning("Databricks parser unable to parse statement, falling back to default statement")

    statement_words_sigs:list[list[str]] = [
        ["CREATE", "PROCEDURE"],
        ["DROP", "PROCEDURE"],
        ["CREATE", "CATALOG"],
        ["DROP", "CATALOG"],
        ["CREATE", "VOLUME"],
        ["DROP", "VOLUME"]
    ]
    # standardise white space
    sql_words = sql.upper().split()

    for statement_words in statement_words_sigs:
        _default_statement = _create_statement(statement_words=statement_words, sql_words=sql_words)
        statements[0][_STATEMENT_KEY] = _default_statement
        if statements[0][_STATEMENT_KEY]:
            log.info(f"Databricks parser unable to parse statement, defaulted to statement {_default_statement}")
            # found it so bail
            return statements
    
    log.info("Databricks parser unable to parse statement, unable to parse default statement, unknown statement")
    return statements
