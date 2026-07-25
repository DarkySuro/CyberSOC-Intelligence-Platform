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
    "autocommit": True
}

def get_connection():
    conn = connector.connect(**DB_CONFIG)

    try:
        with open('soc.sql', 'r') as file:
            sql_file = file.read()

        cursor = conn.cursor()
        print('Executing SQL file batches...')
         # multi=True easily parses triggers and complex blocks without client delimiters
        for result in cursor.execute(sql_file, multi=True):
            # Safely consume any metadata or returned rows to prevent sync bugs
            if result.with_rows:
                result.fetchall()
        return conn
    except:
        print('Database cannot be created!')
        if conn.is_connected():
            cursor.close()
            conn.close()
        

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