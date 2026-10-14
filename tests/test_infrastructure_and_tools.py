import sys
import os
import redis
import psycopg2
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.llm.adapter import search_products, get_categories, search_by_price, search_exact, recommend_similar_products

def test_infrastructure_and_tools():
    print("\n=================== INFRASTRUCTURE & TOOLS CHECK ===================")
    
    # 1. Check PostgreSQL
    print("\n[1] Checking PostgreSQL connection...")
    try:
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME")
        
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print(f"  [OK] PostgreSQL connected successfully! Version: {db_version[0][:40]}...")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"  [ERROR] PostgreSQL connection failed: {e}")

    # 2. Check Redis
    print("\n[2] Checking Redis connection...")
    try:
        r = redis.Redis(host='localhost', port=6379, db=0, socket_timeout=2)
        r.ping()
        print("  [OK] Redis connected successfully!")
    except Exception as e:
        print(f"  [ERROR] Redis connection failed (is Redis service running?): {e}")

    # 3. Check LLM Tools
    print("\n[3] Checking LLM Tools initialization...")
    try:
        tools = [search_products, get_categories, search_by_price, search_exact, recommend_similar_products]
        print(f"  [OK] Successfully loaded {len(tools)} tools:")
        for tool in tools:
            print(f"    - Tool Name: {tool.name}")
            print(f"      Description: {tool.description[:60]}...")
    except Exception as e:
        print(f"  [ERROR] Failed to load tools: {e}")

    print("\n====================================================================")

if __name__ == "__main__":
    test_infrastructure_and_tools()
