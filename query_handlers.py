import os
import mysql.connector as connector
import pandas as pd
from dotenv import load_dotenv,find_dotenv

load_dotenv(find_dotenv(), override=True)

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

def get_connection():
    return connector.connect(**DB_CONFIG)

def run_query(sql: str, params: tuple | None = None) -> pd.DataFrame:
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            rows = cursor.fetchall()
        return pd.DataFrame(rows)
    finally:
        conn.close()

def run_write(sql: str, params: tuple | None = None) -> int:
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            affected = cursor.execute(sql, params or ())
        conn.commit()
        return affected
    finally:
        conn.close()

def call_procedure(proc_name: str, params: tuple = ()) -> list[pd.DataFrame]:
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.callproc(proc_name, params)
            results = [pd.DataFrame(cursor.fetchall())]
            while cursor.nextset():
                results.append(pd.DataFrame(cursor.fetchall()))
        conn.commit()
        return [df for df in results if not df.empty]
    finally:
        conn.close()