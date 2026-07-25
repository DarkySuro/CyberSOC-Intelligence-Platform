import os
import re
import mysql.connector as connector
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "autocommit": True,
}

_COMPOUND_CLOSERS = {"IF", "WHILE", "LOOP", "REPEAT", "CASE"}


def split_sql_statements(sql_text: str) -> list[str]:
    """
    Split a SQL script into individual executable statements without relying
    on the connector's multi=True mode (unsupported by the C-extension
    cursor in newer mysql-connector-python, and even on the pure-Python
    cursor it doesn't understand BEGIN...END routine bodies with their own
    internal semicolons).

    Rules implemented:
    - Semicolons inside quoted strings don't split statements.
    - A ";" only ends a statement when we're not nested inside a routine's
      BEGIN...END block.
    - "END IF" / "END WHILE" / "END LOOP" / "END REPEAT" / "END CASE" close
      a control-flow block, not the routine's BEGIN, so they don't count
      as closing BEGIN.
    - This script's CREATE TRIGGER / CREATE PROCEDURE bodies have no
      trailing ";" after their final END, so a statement is also finalized
      the instant the outermost BEGIN's matching (non-compound) END is seen.
    """
    # Strip "-- ..." line comments up front.
    sql_text = "".join(
        line for line in sql_text.splitlines(keepends=True)
        if not line.lstrip().startswith("--")
    )
    n = len(sql_text)

    statements = []
    buf = []
    in_squote = False
    in_dquote = False
    depth = 0
    i = 0

    def next_word(pos):
        j = pos
        while j < n and sql_text[j].isspace():
            j += 1
        k = j
        while k < n and (sql_text[k].isalpha() or sql_text[k] == "_"):
            k += 1
        return sql_text[j:k].upper(), k

    def finalize():
        stmt = "".join(buf).strip().rstrip(";").strip()
        buf.clear()
        if stmt:
            statements.append(stmt)

    while i < n:
        ch = sql_text[i]

        if in_squote:
            buf.append(ch)
            if ch == "'" and not (i + 1 < n and sql_text[i + 1] == "'"):
                in_squote = False
            i += 1
            continue
        if in_dquote:
            buf.append(ch)
            if ch == '"' and not (i + 1 < n and sql_text[i + 1] == '"'):
                in_dquote = False
            i += 1
            continue
        if ch == "'":
            in_squote = True
            buf.append(ch)
            i += 1
            continue
        if ch == '"':
            in_dquote = True
            buf.append(ch)
            i += 1
            continue

        if ch.isalpha() or ch == "_":
            # read the whole word
            j = i
            while j < n and (sql_text[j].isalpha() or sql_text[j] == "_"):
                j += 1
            word = sql_text[i:j].upper()
            buf.append(sql_text[i:j])

            if word == "BEGIN":
                depth += 1
            elif word == "END":
                nxt, _ = next_word(j)
                if nxt in _COMPOUND_CLOSERS:
                    pass  # closes IF/WHILE/LOOP/REPEAT/CASE, not BEGIN
                else:
                    depth = max(0, depth - 1)
                    if depth == 0:
                        finalize()
            i = j
            continue

        buf.append(ch)
        if ch == ";" and depth == 0:
            finalize()
        i += 1

    tail = "".join(buf).strip().rstrip(";").strip()
    if tail:
        statements.append(tail)

    return statements


def db_exists(db_name: str | None = None) -> bool:
    """
    Return True if the target database already exists and is reachable,
    False if it genuinely doesn't exist yet (MySQL error 1049 / ER_BAD_DB_ERROR).
    Any other connection error (bad host, bad credentials, server down) is
    re-raised, since that's not something init_db() can fix.
    """
    db_name = db_name or os.getenv("DB_NAME", "SecurityOpsCenter")
    try:
        conn = connector.connect(**DB_CONFIG, database=db_name)
        conn.close()
        return True
    except connector.Error as e:
        if e.errno == 1049:  # ER_BAD_DB_ERROR - "Unknown database"
            return False
        raise


def ensure_db_initialized():
    """
    Create and seed the database only if it doesn't already exist.
    Safe to call on every app startup - won't touch an existing database
    (init_db() itself still does DROP+CREATE, but this wrapper only calls
    it when there's nothing there yet, so existing data is never wiped by
    a normal app restart).
    """
    if not db_exists():
        print("Database not found - running first-time initialization...")
        init_db()
    else:
        print("Database already initialized - skipping setup.")


def init_db():
    """
    Drops, creates, and seeds the database using the .sql file.
    """
    print("Connecting to MySQL server...")
    conn = connector.connect(**DB_CONFIG)

    try:
        with open("soc.sql", "r", encoding="utf-8") as file:
            sql_file = file.read()

        statements = split_sql_statements(sql_file)
        print(f"Executing {len(statements)} SQL statements...")

        cursor = conn.cursor()
        for idx, stmt in enumerate(statements, start=1):
            try:
                cursor.execute(stmt)
                if cursor.with_rows:
                    cursor.fetchall()
                # A CALL to a stored procedure can return more than one
                # result set (its own SELECT(s) plus a trailing status
                # result). Every one of them must be drained before the
                # next statement is sent, or the connection gets confused
                # ("Commands out of sync; you can't run this command now").
                while True:
                    try:
                        has_more = cursor.nextset()
                    except connector.Error:
                        break
                    if not has_more:
                        break
                    if cursor.with_rows:
                        cursor.fetchall()
            except connector.Error as e:
                print(f"[Statement {idx} failed] {e}\n--- statement was ---\n{stmt[:200]}...\n")
                raise
        print("Database initialization complete.")
    except Exception as e:
        print(f"Database initialization failed: {e}")
        raise  # let callers (e.g. app.py) know init failed instead of silently continuing
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    init_db()
