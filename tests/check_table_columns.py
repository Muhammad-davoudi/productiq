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
    
    for table in ['kafka_sentiment_results', 'kafka_clustering_results']:
        cur.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table}';
        """)
        columns = cur.fetchall()
        print(f"\n--- Columns in {table} ---")
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")
            
    cur.close()
    conn.close()
except Exception as e:
    print(f"[ERROR] {e}")
