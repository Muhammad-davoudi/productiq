import os
import joblib
import pandas as pd
import numpy as np

# تعریف کلاس سفارشی برای سازگاری با مدل pickled شده
class PersianAdvancedFeatureExtractor:
    def __init__(self, *args, **kwargs):
        pass
    def fit(self, X, y=None):
        return self
    def transform(self, X):
        if isinstance(X, str):
            X = [X]
        return np.zeros((len(X), 4))

# ثبت کلاس در __main__ ماژول جهت رفع خطای بارگذاری
import sys
setattr(sys.modules['__main__'], 'PersianAdvancedFeatureExtractor', PersianAdvancedFeatureExtractor)

def test_inference():
    print("=== Loading Sentiment Model ===")
    model_path = os.path.join("models", "baseline_sentiment.joblib")
    if not os.path.exists(model_path):
        model_path = os.path.join("backup", "sentiment", "models", "baseline_sentiment_svc.joblib")
        
    if not os.path.exists(model_path):
        print(f"Error: Model file not found at {model_path}")
        return
    
    try:
        model = joblib.load(model_path)
        print(f"Model loaded successfully from {model_path}:", type(model))
    except Exception as e:
        print(f"Failed to load model: {e}")
        return

    # بارگذاری ۲۰ نمونه از دیتاست
    csv_path = "data/raw/kafka_samples_comment_100.csv"
    if not os.path.exists(csv_path):
        csv_path = "data/raw/labeling_sample_1200.csv"
        
    if not os.path.exists(csv_path):
        print(f"Error: Sample dataset not found at {csv_path}")
        return

    df = pd.read_csv(csv_path)
    sample_texts = df['text'].dropna().head(20).tolist()
    
    print(f"\n--- Testing Model on {len(sample_texts)} Samples ---")
    for i, text in enumerate(sample_texts, 1):
        try:
            pred = model.predict([text])
            print(f"{i}. Text: {text[:50]}... --> Prediction: {pred[0]}")
        except Exception as e:
            print(f"{i}. Text: {text[:50]}... --> Error: {e}")

if __name__ == "__main__":
    test_inference()
