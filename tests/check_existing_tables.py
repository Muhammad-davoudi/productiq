import os
import psycopg2
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

try:
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME", "digikala_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432")
    )
    cur = conn.cursor()
    
    # استخراج نام تمام جداول در اسکیما عمومی (public)
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public';
    """)
    tables = cur.fetchall()
    
    print("--- Existing Tables in PostgreSQL (digikala_db) ---")
    if tables:
        for t in tables:
            print(f"- {t[0]}")
    else:
        print("No tables found in public schema.")
        
    cur.close()
    conn.close()
except Exception as e:
    print(f"[ERROR] Could not connect or query PostgreSQL: {e}")

if __name__ == "__main__":
    pass
