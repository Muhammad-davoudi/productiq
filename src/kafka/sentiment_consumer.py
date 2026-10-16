import os
import sys
import json
import psycopg2
from kafka import KafkaConsumer
from dotenv import load_dotenv

# ایمپورت پیش‌بینی‌کننده استاندارد احساسات
from src.models.predict import SentimentPredictor

load_dotenv()

_predictor = None

def get_predictor():
    global _predictor
    if _predictor is None:
        _predictor = SentimentPredictor()
    return _predictor

def get_db_connection():
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return psycopg2.connect(db_url)
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "digikala_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 5432))
    )

def extract_review_text(data: dict) -> str:
    if not isinstance(data, dict):
        return ""
    for field in ("comment", "text", "body", "comment_text", "content"):
        val = data.get(field)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""

def process_sentiment_message(data: dict) -> tuple[str, str, float]:
    review_id = str(data.get("id") or data.get("review_id") or "")
    text = extract_review_text(data)

    if not text:
        return review_id, "neutral", 1.0

    predictor = get_predictor()
    # ارسال مستقیم متن به Predictor (خروجی مستقیم رشته: positive, negative, neutral)
    sentiment_label = predictor.predict(text)

    score_map = {
        "positive": 2.0,
        "neutral": 1.0,
        "negative": 0.0
    }
    score = score_map.get(sentiment_label, 1.0)

    return review_id, sentiment_label, score

def save_to_db(review_id: str, sentiment: str, score: float):
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
        consumer_timeout_ms=15000,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    print("[INFO] Sentiment Consumer started and waiting for messages...")
    for message in consumer:
        try:
            print(f"[RECEIVED] Raw message: {message.value}")
            review_id, sentiment, score = process_sentiment_message(message.value)
            save_to_db(review_id, sentiment, score)
            consumer.commit()
            print(f"[OK] Processed sentiment for review_id='{review_id}' -> sentiment='{sentiment}' (score={score})")
        except Exception as exc:
            print(f"[ERROR] Error handling Kafka message: {exc}", file=sys.stderr)

    print("[INFO] Consumer finished (timeout reached or no more messages).")

if __name__ == "__main__":
    run_consumer()
