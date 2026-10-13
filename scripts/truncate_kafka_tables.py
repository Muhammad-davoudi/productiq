import os
from pathlib import Path
import psycopg2
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME", "digikala_db"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", ""),
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", 5432)
)
cur = conn.cursor()

# پاک‌سازی کامل جداول کافکا و ریست کردن آی‌دی‌ها
cur.execute("""
TRUNCATE TABLE 
    kafka_clustering_results, 
    kafka_sentiment_results, 
    kafka_evaluation_runs 
RESTART IDENTITY CASCADE;
""")

conn.commit()
print("All Kafka tables truncated and ID sequences reset successfully!")

# بررسی مجدد تعداد سطرها
tables = ["kafka_clustering_results", "kafka_sentiment_results", "kafka_evaluation_runs"]
print("-" * 50)
for t in tables:
    cur.execute(f'SELECT COUNT(*) FROM "{t}";')
    print(f"{t:<30}: {cur.fetchone()[0]} rows")
print("-" * 50)

cur.close()
conn.close()
