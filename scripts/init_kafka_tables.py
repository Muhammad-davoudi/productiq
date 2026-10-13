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

cur.execute("""
CREATE TABLE IF NOT EXISTS kafka_evaluation_runs (
    id SERIAL PRIMARY KEY,
    status VARCHAR(50) DEFAULT 'running',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS kafka_sentiment_results (
    id SERIAL PRIMARY KEY,
    review_id VARCHAR(100),
    sentiment VARCHAR(50),
    confidence FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS kafka_clustering_results (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(100),
    cluster_label INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

conn.commit()
cur.close()
conn.close()
print("Kafka evaluation tables created successfully!")
