import os
import mysql.connector as connector
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "autocommit": True
}

def init_db():
    """
    Drops, creates, and seeds the database using the .sql file.
    """
    print("Connecting to MySQL server...")
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
    except Exception as e:
        print(f'Database initialization failed: {e}')
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    init_db()