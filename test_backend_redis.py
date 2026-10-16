import os
from dotenv import load_dotenv
import redis
import psycopg2

load_dotenv()

print("=== Checking Redis Connection ===")
try:
    r = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        socket_timeout=2
    )
    r.ping()
    print("Redis connection: SUCCESS")
except Exception as e:
    print(f"Redis connection: FAILED ({e})")

print("\n=== Checking Database Connection ===")
try:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 5432)),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        dbname=os.getenv("DB_NAME", "digikala_db"),
        connect_timeout=2
    )
    conn.close()
    print("Database connection: SUCCESS")
except Exception as e:
    print(f"Database connection: FAILED ({e})")
