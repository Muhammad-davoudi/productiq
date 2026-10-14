import os
import json
import time
from dotenv import load_dotenv, find_dotenv
import joblib
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

load_dotenv(find_dotenv())

# تعریف کلاس استخراج ویژگی که مدل برای بارگذاری به آن نیاز دارد
class PersianAdvancedFeatureExtractor(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass
    def fit(self, X, y=None):
        return self
    def transform(self, X):
        features = []
        for text in X:
            t = str(text) if text is not None else ""
            length = len(t)
            word_count = len(t.split())
            exclamation_count = t.count('!')
            question_count = t.count('؟') + t.count('?')
            features.append([length, word_count, exclamation_count, question_count])
        return np.array(features, dtype=float)

try:
    from kafka import KafkaProducer, KafkaConsumer
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False

def test_kafka_pipeline():
    if not KAFKA_AVAILABLE:
        print("[SKIP] kafka-python package is not installed.")
        return

    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    topic_name = "digikala-user-reviews"

    print(f"[INFO] Connecting to Kafka at {bootstrap_servers}...")
    
    # ۱. بارگذاری مدل تحلیل احساسات
    model_path = "models/baseline_sentiment.joblib"
    if os.path.exists(model_path):
        sentiment_model = joblib.load(model_path)
        print("[OK] Sentiment model loaded successfully for Kafka consumer test.")
    else:
        print(f"[WARN] Model not found at {model_path}, using mock prediction.")
        sentiment_model = None

    try:
        # ۲. ایجاد Producer برای ارسال پیام تستی
        producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            request_timeout_ms=3000
        )
        
        test_message = {"review_id": 101, "comment": "محصول بسیار عالی و باکیفیتی بود، ممنون از دیجی‌کالا"}
        producer.send(topic_name, test_message)
        producer.flush()
        print(f"[OK] Sent test message to topic '{topic_name}': {test_message}")

    except Exception as e:
        print(f"[ERROR] Could not connect to Kafka broker. Is Kafka running? Error: {e}")
        return

    # ۳. شبیه‌سازی Consumer و پردازش با مدل
    try:
        consumer = KafkaConsumer(
            topic_name,
            bootstrap_servers=bootstrap_servers,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='test-sentiment-group',
            consumer_timeout_ms=4000,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )

        print("[INFO] Listening for messages to process with sentiment model...")
        message_processed = False
        
        for message in consumer:
            data = message.value
            comment = data.get("comment", "")
            print(f"[RECEIVED] Raw message: {data}")

            # اعمال مدل هوش مصنوعی
            if sentiment_model:
                try:
                    pred = sentiment_model.predict([comment])
                    sentiment_label = int(pred[0])
                    print(f"[AI MODEL] Sentiment prediction for comment: Class {sentiment_label} (0: Neg, 1: Neu, 2: Pos)")
                except Exception as model_err:
                    print(f"[ERROR] Model prediction failed: {model_err}")
            else:
                print("[AI MODEL] Model bypassed (not found).")

            message_processed = True
            break

        if not message_processed:
            print("[WARN] No messages consumed within timeout.")

        consumer.close()

    except Exception as e:
        print(f"[ERROR] Consumer execution failed: {e}")

if __name__ == "__main__":
    test_kafka_pipeline()
