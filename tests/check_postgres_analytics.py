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
    
    # بررسی وجود جدول و تعداد رکوردهای آن
    cur.execute("SELECT COUNT(*) FROM review_analytics;")
    count = cur.fetchone()[0]
    print(f"[OK] Table 'review_analytics' exists and has {count} records.")
    
    # نمایش آخرین رکوردها
    cur.execute("SELECT id, review_id, comment, sentiment_label, cluster_id, created_at FROM review_analytics ORDER BY id DESC LIMIT 5;")
    rows = cur.fetchall()
    print("\n--- Recent Analytics Records in PostgreSQL ---")
    for row in rows:
        print(f"ID: {row[0]} | Review ID: {row[1]} | Sentiment: {row[3]} | Cluster: {row[4]} | Comment: {row[2][:40]}...")
        
    cur.close()
    conn.close()
except Exception as e:
    print(f"[ERROR] Could not query PostgreSQL: {e}")

if __name__ == "__main__":
    pass
