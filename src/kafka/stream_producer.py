import os
import json
import time
import argparse
import pandas as pd
from kafka import KafkaProducer
from dotenv import load_dotenv

load_dotenv()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, default=1, help="Batch size for streaming")
    args = parser.parse_args()

    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8')
    )

    comment_file = "input_kafka_comment_sample.csv"
    product_file = "product_kafka.csv"

    comments = []
    products = []

    if os.path.exists(comment_file):
        df_c = pd.read_csv(comment_file)
        comments = df_c.to_dict(orient="records")

    if os.path.exists(product_file):
        df_p = pd.read_csv(product_file)
        products = df_p.to_dict(orient="records")

    print(f"[INFO] Starting stream simulation... (Comments: {len(comments)}, Products: {len(products)})")

    max_len = max(len(comments), len(products))

    for i in range(0, max_len, args.batch_size):
        # ارسال بچ کامنت‌ها
        for c in comments[i:i + args.batch_size]:
            msg = {
                "review_id": str(c.get("id", i)),
                "comment": str(c.get("comment", c.get("body", ""))),
                "title": str(c.get("title", ""))
            }
            producer.send("digikala-user-reviews", value=msg)
            print(f"[SENT COMMENT] ID: {msg['review_id']} | Text: {msg['comment'][:40]}...")

        # ارسال بچ محصولات
        for p in products[i:i + args.batch_size]:
            producer.send("digikala-product-stream", value=p)
            print(f"[SENT PRODUCT] ID: {p.get('id', i)} | Title: {str(p.get('title', ''))[:40]}...")

        producer.flush()
        time.sleep(2.0)  # مکث ۲ ثانیه‌ای برای دیدن جریان

    print("[INFO] Stream simulation finished.")

if __name__ == "__main__":
    main()
