import os
import json
import logging
import psycopg2
from kafka import KafkaConsumer
from src.models.predict import SentimentPredictor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC_NAME = "digikala-comments"
GROUP_ID = "digikala-sentiment-consumer"

def get_db_connection():
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return psycopg2.connect(db_url)
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "digikala_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgrespassword"),
        host=os.getenv("DB_HOST", "db"),
        port=int(os.getenv("DB_PORT", 5432))
    )

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS kafka_sentiment_results (
                id SERIAL PRIMARY KEY,
                sentiment VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cur.execute("""
            ALTER TABLE kafka_sentiment_results ADD COLUMN IF NOT EXISTS comment_text TEXT;
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to init sentiment DB table: {e}")

def run_sentiment_consumer():
    init_db()
    logger.info(f"Starting Kafka consumer on bootstrap='{KAFKA_BOOTSTRAP_SERVERS}', topic='{TOPIC_NAME}', group_id='{GROUP_ID}'")
    predictor = SentimentPredictor()
    
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id=GROUP_ID,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    
    conn = get_db_connection()
    cur = conn.cursor()

    logger.info("Sentiment Consumer started and waiting for messages...")
    for message in consumer:
        data = message.value
        comment_text = data.get("comment", "") or data.get("body", "") or data.get("text", "")
        if comment_text:
            pred = predictor.predict(comment_text)
            sentiment_label = pred.get("sentiment", "neutral") if isinstance(pred, dict) else str(pred)
            
            try:
                cur.execute(
                    "INSERT INTO kafka_sentiment_results (comment_text, sentiment) VALUES (%s, %s);",
                    (comment_text, sentiment_label.lower())
                )
                conn.commit()
            except Exception as db_err:
                conn.rollback()
                logger.error(f"DB insert error: {db_err}")

            logger.info(f"Processed comment -> Sentiment: {sentiment_label}")

if __name__ == "__main__":
    run_sentiment_consumer()
