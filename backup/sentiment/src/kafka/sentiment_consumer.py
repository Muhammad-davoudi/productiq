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
    Process sentiment for a single review message using verified Phase 2 model.
    Returns: (review_id, sentiment_label, score)
    """
    review_id = str(data.get("id") or data.get("review_id") or "")
    text = extract_review_text(data)

    if not text:
        # If text is empty or missing, predict pipeline contract returns Uncertain
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
    consumer = KafkaConsumer(
        'raw_reviews',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='latest',
        enable_auto_commit=False,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    print("Sentiment Consumer started and waiting for messages...")
    for message in consumer:
        try:
            review_id, sentiment, score = process_sentiment_message(message.value)
            save_to_db(review_id, sentiment, score)
            consumer.commit()
            print(f"Processed sentiment for review: {review_id} -> {sentiment}")
        except Exception as exc:
            print(f"Error handling Kafka message: {exc}")


if __name__ == "__main__":
    run_consumer()
