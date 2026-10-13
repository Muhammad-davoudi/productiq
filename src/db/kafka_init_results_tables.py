import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def init_tables():
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME", "digikala_db"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost")
    )
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS kafka_evaluation_runs (
            id VARCHAR(50) PRIMARY KEY,
            status VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS kafka_sentiment_results (
            id SERIAL PRIMARY KEY,
            review_id VARCHAR(50),
            sentiment TEXT,
            score FLOAT
        );
        CREATE TABLE IF NOT EXISTS kafka_clustering_results (
            id SERIAL PRIMARY KEY,
            product_id VARCHAR(50),
            cluster_label INT
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("Kafka tables initialized.")

if __name__ == "__main__":
    init_tables()
