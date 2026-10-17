import os
import sys
import json
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

def main():
    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    topic = "digikala-product-stream"
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
        print(f"[WARN] Could not load clustering model: {e}. Using dummy cluster assignment.")
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

            cluster_label = "cluster_0"
            if cluster_model is not None:
                try:
                    pred = cluster_model.predict([title])
                    cluster_label = str(pred[0])
                except Exception:
                    cluster_label = f"cluster_{hash(title) % 6}"

            try:
                cursor.execute(
                    """
                    INSERT INTO kafka_clustering_results (product_id, cluster_label)
                    VALUES (%s, %s)
                    """,
                    (product_id, cluster_label)
                )
                conn.commit()
                print(f"[OK] Processed clustering for product_id='{product_id}' -> cluster={cluster_label}")
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
