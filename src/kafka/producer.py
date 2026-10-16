import json
import time
import pandas as pd
from kafka import KafkaProducer
from kafka.errors import KafkaError

BOOTSTRAP_SERVERS = 'localhost:9092'
TOPIC_NAME = 'digikala-user-reviews'

def create_producer():
    try:
        producer = KafkaProducer(
            bootstrap_servers=BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8')
        )
        print(f"[INFO] Connected to Kafka at {BOOTSTRAP_SERVERS}")
        return producer
    except Exception as e:
        print(f"[ERROR] Failed to connect to Kafka: {e}")
        return None

def main():
    producer = create_producer()
    if not producer:
        return

    csv_path = 'data/raw/kafka_samples_comment_100.csv'
    try:
        df = pd.read_csv(csv_path)
        print(f"[INFO] Loaded {len(df)} records from {csv_path}")
    except Exception as e:
        print(f"[ERROR] Failed to load CSV: {e}")
        return

    print(f"[INFO] Starting to stream records to topic '{TOPIC_NAME}'...")
    
    for idx, row in df.iterrows():
        message = {
            "review_id": str(row.get('id', idx)),
            "comment": str(row.get('text', '')),
            "title": f"Rate: {row.get('rate', 'N/A')}"
        }
        
        try:
            producer.send(TOPIC_NAME, value=message)
            print(f"[SENT] review_id={message['review_id']} | rate={row.get('rate')} | comment={message['comment'][:40]}...")
            producer.flush()
        except KafkaError as ke:
            print(f"[ERROR] Kafka send failed: {ke}")
        
        time.sleep(1.0)

    print("[INFO] Finished streaming all samples.")

if __name__ == '__main__':
    main()
