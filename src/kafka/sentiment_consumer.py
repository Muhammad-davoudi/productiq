import json
import ast
import os
import psycopg2
from kafka import KafkaConsumer
from dotenv import load_dotenv

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

consumer = KafkaConsumer(
    'raw_reviews',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='latest',
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

def extract_sentiment_and_score(data):
    # اولویت ۱: اگر قبلاً فیلد صریح وجود داشت
    if 'sentiment' in data and data['sentiment']:
        sent = str(data['sentiment']).lower()
        score = float(data.get('score', 0.85))
        return sent, score

    # اولویت ۲: استخراج از ستون label مثل "{'final': 'Positive'}"
    raw_label = data.get('label')
    if raw_label:
        try:
            if isinstance(raw_label, str) and (raw_label.startswith('{') or raw_label.startswith('[')):
                parsed = ast.literal_eval(raw_label)
                if isinstance(parsed, dict):
                    val = parsed.get('final') or parsed.get('sentiment') or list(parsed.values())[0]
                    val_str = str(val).lower()
                    if 'pos' in val_str:
                        return 'positive', 0.90
                    elif 'neg' in val_str:
                        return 'negative', 0.88
                    else:
                        return 'neutral', 0.75
            val_str = str(raw_label).lower()
            if 'pos' in val_str or val_str == '1':
                return 'positive', 0.90
            elif 'neg' in val_str or val_str == '-1' or val_str == '0':
                return 'negative', 0.88
            return 'neutral', 0.75
        except Exception:
            pass

    return 'neutral', 0.70

def save_to_db(data):
    review_id = str(data.get('id', ''))
    sentiment, score = extract_sentiment_and_score(data)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO kafka_sentiment_results (review_id, sentiment, score) VALUES (%s, %s, %s)",
        (review_id, sentiment, score)
    )
    conn.commit()
    cur.close()
    conn.close()

print("Sentiment Consumer started and waiting for messages...")
for message in consumer:
    save_to_db(message.value)
    print(f"Processed sentiment for review: {message.value.get('id')}")
