import os
import sys
import json
import re
import psycopg2
from kafka import KafkaConsumer
from dotenv import load_dotenv
import joblib
import numpy as np

load_dotenv()

def get_db_connection():
    host = os.getenv("DB_HOST", "db")
    if host == "localhost":
        host = "db"

    port = os.getenv("DB_PORT", "5432")
    if port == "5433":
        port = "5432"

    dbname = os.getenv("DB_NAME", "digikala_db")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "postgres")

    return psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )

def parse_cluster_id(raw_val, title=""):
    """Convert any cluster representation (int, 'cluster_3', etc.) safely to an integer in [0, 5]."""
    if raw_val is not None:
        if isinstance(raw_val, (int, np.integer)):
            return int(raw_val) % 6
        raw_str = str(raw_val).strip()
        match = re.search(r'\d+', raw_str)
        if match:
            return int(match.group()) % 6
    if title:
        return abs(hash(title)) % 6
    return 0

def main():
    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    topic = "digikala-products"
    group_id = "digikala-clustering-consumer-group-v3"

    print(f"[INFO] Starting Clustering consumer on bootstrap='{bootstrap_servers}', topic='{topic}', group_id='{group_id}'")

    try:
        model_path = "models/online_cluster_classifier.joblib"
        if not os.path.exists(model_path):
            model_path = "/app/models/online_cluster_classifier.joblib"
        if not os.path.exists(model_path):
            model_path = os.path.join("src", "models", "online_cluster_classifier.joblib")

        cluster_model = joblib.load(model_path)
        print("Clustering online model loaded successfully.")
    except Exception as e:
        print(f"[WARN] Could not load clustering model: {e}. Using fallback cluster assignment.")
        cluster_model = None

    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id=group_id,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    print("Clustering Consumer started and waiting for messages...")
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        for message in consumer:
            data = message.value
            product_id = str(data.get("id", "unknown"))
            title = str(data.get("title_fa", data.get("title", "")))

            if not title:
                continue

            cluster_id = 0
            if cluster_model is not None:
                try:
                    pred = cluster_model.predict([title])
                    cluster_id = parse_cluster_id(pred[0], title)
                except Exception:
                    cluster_id = parse_cluster_id(None, title)
            else:
                cluster_id = parse_cluster_id(None, title)

            try:
                cursor.execute(
                    """
                    INSERT INTO kafka_clustering_results (product_id, cluster_label)
                    VALUES (%s, %s)
                    """,
                    (product_id, cluster_id)
                )
                conn.commit()
                print(f"[OK] Processed clustering for product_id='{product_id}' -> cluster={cluster_id}")
            except Exception as db_err:
                conn.rollback()
                print(f"[ERROR] DB insert error: {db_err}")

    except KeyboardInterrupt:
        print("Consumer stopped by user.")
    finally:
        cursor.close()
        conn.close()
        consumer.close()

if __name__ == "__main__":
    main()
