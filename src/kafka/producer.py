import pandas as pd
import json
import time
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

def stream_data():
    reviews = pd.read_csv('input_kafka_comment.csv')
    products = pd.read_csv('product_kafka.csv')

    print("Starting stream...")
    for i in range(len(reviews)):
        # ارسال نقد
        review = reviews.iloc[i].to_dict()
        producer.send('raw_reviews', value=review)
        
        # ارسال محصول (هر ۱۰ نقد، یک محصول - برای شبیه‌سازی)
        if i % 10 == 0:
            prod = products.iloc[i % len(products)].to_dict()
            producer.send('raw_products', value=prod)
        
        time.sleep(0.5)  # تاخیر برای نمایش بهتر در مصرف‌کننده‌ها
        if i % 50 == 0: print(f"Sent {i} records...")

    producer.flush()
    print("Stream finished.")

if __name__ == "__main__":
    stream_data()
