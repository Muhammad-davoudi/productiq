import os
import json
import time
import argparse
import pandas as pd
from kafka import KafkaProducer
from dotenv import load_dotenv

load_dotenv()

def find_data_file(filename):
    possible_paths = [
        os.path.join("/app/data/raw", filename),
        os.path.join("data/raw", filename),
        os.path.join("/app", filename),
        filename
    ]
    for p in possible_paths:
        if os.path.exists(p):
            return p
    return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, default=1, help="Batch size for streaming")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between batches in seconds")
    args = parser.parse_args()

    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    producer = None

    # Retry connecting to Kafka
    for _ in range(5):
        try:
            producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8')
            )
            break
        except Exception as e:
            print(f"[WARN] Kafka Producer connection retry due to: {e}")
            time.sleep(2)

    if not producer:
        print("[ERROR] Failed to connect to Kafka producer.")
        return

    comment_path = find_data_file("kafka_samples_comment_100.csv")
    product_path = find_data_file("product_kafka_sample.csv")

    comments = []
    products = []

    if comment_path:
        print(f"[INFO] Loading comments from: {comment_path}")
        df_c = pd.read_csv(comment_path)
        comments = df_c.to_dict(orient="records")
    else:
        print("[WARN] Comment sample file not found in searched paths.")

    if product_path:
        print(f"[INFO] Loading products from: {product_path}")
        df_p = pd.read_csv(product_path)
        products = df_p.to_dict(orient="records")
    else:
        print("[WARN] Product sample file not found in searched paths.")

    print(f"[INFO] Starting stream simulation... (Comments: {len(comments)}, Products: {len(products)})")

    max_len = max(len(comments), len(products))

    for i in range(0, max_len, args.batch_size):
        # Stream comments batch
        if i < len(comments):
            batch_comments = comments[i:i + args.batch_size]
            for c in batch_comments:
                producer.send("digikala-comments", c)

        # Stream products batch
        if i < len(products):
            batch_products = products[i:i + args.batch_size]
            for p in batch_products:
                producer.send("digikala-products", p)

        producer.flush()
        time.sleep(args.delay)

    print("[INFO] Stream simulation completed successfully.")

if __name__ == "__main__":
    main()
