import os
import json
import psycopg2
from kafka import KafkaConsumer
from dotenv import load_dotenv

from src.models.predict import analyze_review

load_dotenv()


def get_db_connection():
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return psycopg2.connect(db_url)
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "digikala_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", 5432)
    )


def extract_review_text(data: dict) -> str:
    """Extract review text body from incoming kafka message dictionary."""
    if not isinstance(data, dict):
        return ""
    for field in ("comment", "text", "body", "comment_text", "content"):
        val = data.get(field)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def process_sentiment_message(data: dict) -> tuple[str, str, float | None]:
    """
    Process sentiment for a single review message using verified model pipeline.
    Returns: (review_id, sentiment_label, score)
    """
    review_id = str(data.get("id") or data.get("review_id") or "")
    text = extract_review_text(data)

    if not text:
        return review_id, "Uncertain", None

    try:
        result = analyze_review(text)
        sentiment_label = result.get("final", "Uncertain")
        return review_id, sentiment_label, None
    except Exception as exc:
        print(f"Inference failure for review_id '{review_id}': {exc}")
        return review_id, "InferenceError", None


def save_to_db(review_id: str, sentiment: str, score: float | None):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO kafka_sentiment_results (review_id, sentiment, score) VALUES (%s, %s, %s)",
            (review_id, sentiment, score)
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()


def run_consumer():
    kafka_bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    kafka_topic = os.getenv("KAFKA_TOPIC", "digikala-user-reviews")
    kafka_group_id = os.getenv("KAFKA_GROUP_ID", "digikala-sentiment-consumer")

    print(f"[INFO] Starting Kafka consumer on bootstrap='{kafka_bootstrap}', topic='{kafka_topic}', group_id='{kafka_group_id}'")

    consumer = KafkaConsumer(
        kafka_topic,
        bootstrap_servers=[kafka_bootstrap],
        auto_offset_reset='latest',
        enable_auto_commit=False,
        group_id=kafka_group_id,
        consumer_timeout_ms=10000,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    print("[INFO] Sentiment Consumer started and waiting for messages...")
    for message in consumer:
        try:
            print(f"[RECEIVED] Raw message: {message.value}")
            review_id, sentiment, score = process_sentiment_message(message.value)
            save_to_db(review_id, sentiment, score)
            consumer.commit()
            print(f"[OK] Processed sentiment for review_id='{review_id}' -> sentiment='{sentiment}'")
        except Exception as exc:
            print(f"[ERROR] Error handling Kafka message: {exc}")

    print("[INFO] Consumer finished (timeout reached or no more messages).")


if __name__ == "__main__":
    run_consumer()
