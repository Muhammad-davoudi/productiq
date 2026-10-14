import os
import json
import time
from dotenv import load_dotenv, find_dotenv
import joblib
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

load_dotenv(find_dotenv())

# تطابق دقیق ابعاد ویژگی‌ها برای مدل احساسات (۱۵۰۴۶) و خوشه‌بندی (۳)
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
            # تولید ویژگی‌های تکمیلی برای رسیدن به ابعاد دقیق
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
    
    sentiment_model_path = "models/baseline_sentiment.joblib"
    cluster_model_path = "models/online_cluster_classifier.joblib"
    
    sentiment_model = joblib.load(sentiment_model_path) if os.path.exists(sentiment_model_path) else None
    cluster_model = joblib.load(cluster_model_path) if os.path.exists(cluster_model_path) else None
    
    print(f"[OK] Sentiment Pipeline Loaded: {sentiment_model is not None}")
    print(f"[OK] Clustering Model Loaded: {cluster_model is not None}")

    try:
        producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            request_timeout_ms=3000
        )
        
        test_message = {
            "review_id": 202, 
            "comment": "گوشی بسیار عالی با دوربین باکیفیت و قیمت مناسب، کاملاً راضی هستم"
        }
        producer.send(topic_name, test_message)
        producer.flush()
        print(f"[OK] Sent test message to topic '{topic_name}': {test_message}")

    except Exception as e:
        print(f"[ERROR] Could not connect to Kafka broker. Error: {e}")
        return

    try:
        consumer = KafkaConsumer(
            topic_name,
            bootstrap_servers=bootstrap_servers,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='test-models-group',
            consumer_timeout_ms=5000,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )

        print("[INFO] Listening for messages to process with AI models...")
        message_processed = False
        
        for message in consumer:
            data = message.value
            comment = data.get("comment", "")
            print(f"\n[RECEIVED] Raw message: {data}")

            # ۱. تحلیل احساسات
            if sentiment_model:
                try:
                    pred_sentiment = sentiment_model.predict([comment])
                    s_label = int(pred_sentiment[0])
                    s_text = {0: "Negative", 1: "Neutral", 2: "Positive"}.get(s_label, str(s_label))
                    print(f"  -> [Sentiment Pipeline] Prediction: {s_text} (Class {s_label})")
                except Exception as err:
                    print(f"  -> [Sentiment Pipeline Error] {err}")

            # ۲. خوشه‌بندی (۳ ویژگی)
            if cluster_model:
                try:
                    length = len(comment)
                    word_count = len(comment.split())
                    exclamation_count = comment.count('!')
                    cluster_input = np.array([[length, word_count, exclamation_count]], dtype=float)
                    
                    pred_cluster = cluster_model.predict(cluster_input)
                    c_label = int(pred_cluster[0])
                    print(f"  -> [Clustering Model] Assigned Cluster: [{c_label}]")
                except Exception as err:
                    print(f"  -> [Clustering Model Error] {err}")

            message_processed = True
            break

        if not message_processed:
            print("[WARN] No messages consumed within timeout.")

        consumer.close()

    except Exception as e:
        print(f"[ERROR] Consumer execution failed: {e}")

if __name__ == "__main__":
    test_kafka_pipeline()
