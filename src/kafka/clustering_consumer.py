import json
import os
import joblib
import numpy as np
import psycopg2
from kafka import KafkaConsumer
from dotenv import load_dotenv

load_dotenv()

# بارگذاری مدل ۶ خوشه‌ای
model_path = "models/online_cluster_classifier.joblib"
model = None

if os.path.exists(model_path):
    try:
        model = joblib.load(model_path)
        print("Clustering online model loaded successfully.")
    except Exception as e:
        print(f"Warning: Could not load model: {e}")

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
    'raw_products',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='latest',
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

def predict_cluster(data):
    # اولویت ۱: اگر شناسه کلاستر در پیام آماده بود
    if 'cluster' in data and data['cluster'] is not None:
        try:
            return int(data['cluster'])
        except Exception:
            pass

    price = float(data.get('Price') or data.get('price') or 0.0)
    rate = float(data.get('Rate') or data.get('rate') or 0.0)
    rate_cnt = float(data.get('Rate_cnt') or data.get('rate_cnt') or 0.0)

    # اولویت ۲: پیش‌بینی با مدل آموزش‌دیده ۶ خوشه‌ای
    if model is not None:
        try:
            X = np.array([[price, rate, rate_cnt]])
            pred = model.predict(X)[0]
            return int(pred)
        except Exception as e:
            pass

    # فال‌بک منطقی بر اساس تفکیک Active و دهک‌های قیمتی پروفایل
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

def save_to_db(data):
    product_id = str(data.get('id', data.get('product_id', '')))
    cluster_label = predict_cluster(data)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO kafka_clustering_results (product_id, cluster_label) VALUES (%s, %s)",
        (product_id, cluster_label)
    )
    conn.commit()
    cur.close()
    conn.close()

print("Clustering Consumer started and waiting for messages...")
for message in consumer:
    save_to_db(message.value)
    print(f"Processed cluster for product: {message.value.get('id', message.value.get('product_id'))} -> Cluster {predict_cluster(message.value)}")
