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

# دریافت لیست تمام جداول public schema
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    ORDER BY table_name;
""")
tables = [row[0] for row in cur.fetchall()]

print("=" * 65)
print(f"{'Table Name':<35} | {'Row Count':>15}")
print("=" * 65)

for table in tables:
    try:
        cur.execute(f'SELECT COUNT(*) FROM "{table}";')
        count = cur.fetchone()[0]
        print(f"{table:<35} | {count:>15,}")
    except Exception as e:
        print(f"{table:<35} | {'ERROR':>15}")

print("=" * 65)
cur.close()
conn.close()
