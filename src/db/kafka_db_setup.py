import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def create_kafka_tables():
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME", "digikala_db"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432")
    )
    cur = conn.cursor()
    
    # Create the table with kafka_ prefix
    cur.execute("""
        CREATE TABLE IF NOT EXISTS kafka_evaluation_runs (
            id VARCHAR(50) PRIMARY KEY,
            status VARCHAR(20),
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            result_summary JSONB
        );
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    print("Table 'kafka_evaluation_runs' created successfully.")

if __name__ == "__main__":
    create_kafka_tables()
