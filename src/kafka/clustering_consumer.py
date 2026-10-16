import os
import json
import joblib
import numpy as np
import psycopg2
from kafka import KafkaConsumer
from dotenv import load_dotenv

load_dotenv()

MODEL_PATH = "models/online_cluster_classifier.joblib"
_model = None

def load_clustering_model(path: str = MODEL_PATH):
    global _model
    if _model is not None:
        return _model
    if os.path.exists(path):
        try:
            _model = joblib.load(path)
            print("Clustering online model loaded successfully.")
        except Exception as e:
            print(f"Warning: Could not load model: {e}")
            _model = None
    else:
        _model = None
    return _model

# بارگذاری اولیه مدل
load_clustering_model()

def get_db_connection():
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return psycopg2.connect(db_url)
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "digikala_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 5433))
    )

def safe_float(value, default: float = 0.0) -> float:
    """Safely convert value to float, handling None and malformed strings."""
    if value is None:
        return default
    try:
        val = float(value)
        if np.isnan(val) or np.isinf(val):
            return default
        return val
    except (ValueError, TypeError):
        return default

def extract_features(data: dict) -> tuple[float, float, float]:
    """Extract price, rate, rate_cnt with fallback keys and safe float parsing."""
    if not isinstance(data, dict):
        return 0.0, 0.0, 0.0

    raw_price = data.get("price") if data.get("price") is not None else data.get("Price")
    raw_rate = data.get("rate") if data.get("rate") is not None else data.get("Rate")
    raw_rate_cnt = data.get("rate_cnt") if data.get("rate_cnt") is not None else data.get("Rate_cnt")

    price = safe_float(raw_price, 0.0)
    rate = safe_float(raw_rate, 0.0)
    rate_cnt = safe_float(raw_rate_cnt, 0.0)

    return price, rate, rate_cnt

def fallback_cluster_rule(price: float, rate: float, rate_cnt: float) -> int:
    """Baseline fallback heuristic based on active status and price percentiles."""
    if rate_cnt > 0 or rate > 0:
        return 0
    if price < 900000:
        return 2
    elif price < 2241000:
        return 4
    elif price < 6501000:
        return 3
    else:
        return 5

def predict_cluster(data: dict, model_instance=None) -> int:
    """
    Predict product cluster using:
    1. Pre-assigned cluster in payload (Priority 1)
    2. Online ML model prediction (Priority 2)
    3. Heuristic fallback (Priority 3)
    """
    if not isinstance(data, dict):
        return fallback_cluster_rule(0.0, 0.0, 0.0)

    if 'cluster' in data and data['cluster'] is not None:
        try:
            return int(data['cluster'])
        except (ValueError, TypeError):
            pass

    price, rate, rate_cnt = extract_features(data)

    clf = model_instance if model_instance is not None else _model
    if clf is None:
        clf = load_clustering_model()

    if clf is not None:
        try:
            X = np.array([[price, rate, rate_cnt]])
            pred = clf.predict(X)[0]
            return int(pred)
        except Exception as e:
            print(f"Inference error in clustering model: {e}")

    return fallback_cluster_rule(price, rate, rate_cnt)

def save_to_db(product_id: str, cluster_label: int):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO kafka_clustering_results (product_id, cluster_label) VALUES (%s, %s)",
            (product_id, cluster_label)
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()

def run_consumer():
    kafka_bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    kafka_topic = os.getenv("KAFKA_CLUSTERING_TOPIC", "digikala-product-stream")
    kafka_group_id = os.getenv("KAFKA_CLUSTERING_GROUP_ID", "digikala-clustering-consumer")

    consumer = KafkaConsumer(
        kafka_topic,
        bootstrap_servers=[kafka_bootstrap],
        auto_offset_reset='latest',
        enable_auto_commit=False,
        group_id=kafka_group_id,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    print("Clustering Consumer started and waiting for messages...")
    for message in consumer:
        try:
            data = message.value
            product_id = str(data.get('id') or data.get('product_id') or '')
            cluster_label = predict_cluster(data)
            save_to_db(product_id, cluster_label)
            consumer.commit()
            print(f"Processed cluster for product: {product_id} -> Cluster {cluster_label}")
        except Exception as exc:
            print(f"Error handling Kafka product message: {exc}")

if __name__ == "__main__":
    run_consumer()
