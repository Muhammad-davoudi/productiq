import os
import joblib
import pandas as pd
import sys

# افزودن مسیر پوشه جاری به پایتون
sys.path.append(os.getcwd())

# ایمپورت مستقیم کلاس اصلی از ساختار پروژه
from src.nlp.feature_engineering import PersianAdvancedFeatureExtractor

def test_inference():
    print("=== Loading Sentiment Model ===")
    model_path = os.path.join("models", "baseline_sentiment.joblib")
    if not os.path.exists(model_path):
        print(f"Error: Model file not found at {model_path}")
        return
    
    try:
        model = joblib.load(model_path)
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Failed to load model: {e}")
        return

    # بارگذاری نمونه‌ها
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
            print(f"{i}. Text: {str(text)[:40]}... --> Prediction: {pred[0]}")
        except Exception as e:
            print(f"{i}. Text: {str(text)[:40]}... --> Error: {e}")

if __name__ == "__main__":
    test_inference()
