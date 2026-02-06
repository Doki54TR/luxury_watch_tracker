import psycopg2
import os

db_host = os.getenv("DB_HOST", "localhost")

DB_PARAMS = {
    "host": db_host,
    "database": "postgres",
    "user": "postgres",
    "password": "1234",
    "port": "5432"
}

try:
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    # It clears all records from the 'prices' table
    cur.execute("TRUNCATE TABLE prices RESTART IDENTITY;")
    
    conn.commit()
    print("🧹 The table is now cleaned. Old prices are deleted.")
    
    cur.close()
    conn.close()
except Exception as e:
    print(e)