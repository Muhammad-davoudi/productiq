import os
import joblib
import pandas as pd
import numpy as np
import sys

# کلاس اصلی استخراج ویژگی با پشتیبانی از صفات لексиکونی مدل بارگذاری شده
class PersianAdvancedFeatureExtractor:
    def __init__(self, *args, **kwargs):
        self.pos_words = kwargs.get('pos_words', set())
        self.neg_words = kwargs.get('neg_words', set())
        self.negation_words = kwargs.get('negation_words', set())

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        if isinstance(X, str):
            X = [X]
        features = []
        for text in X:
            if not isinstance(text, str):
                text = str(text) if text is not None else ""
            
            # استخراج ویژگی‌های لексиکونی منطبق بر مدل اصلی
            text_lower = text.lower()
            pos_count = sum(1 for w in getattr(self, 'pos_words', []) if w in text_lower)
            neg_count = sum(1 for w in getattr(self, 'neg_words', []) if w in text_lower)
            negation_count = sum(1 for w in getattr(self, 'negation_words', []) if w in text_lower)
            
            # اگر ویژگی دیگری مد نظر باشد، به تعداد ۳ ویژگی استاندارد اضافه می شود
            features.append([pos_count, neg_count, negation_count])
            
        return np.array(features, dtype=np.float64)

setattr(sys.modules['__main__'], 'PersianAdvancedFeatureExtractor', PersianAdvancedFeatureExtractor)

def test_inference():
    print("=== Loading Sentiment Model ===")
    model_path = os.path.join("models", "baseline_sentiment.joblib")
    if not os.path.exists(model_path):
        print(f"Error: Model file not found at {model_path}")
        return
    
    try:
        model = joblib.load(model_path)
        print("Model loaded successfully!")
        
        # استخراج شیء lexicon واقعی از درون مدل برای استفاده از کلمات آن
        lexicon_obj = model.named_steps['features'].transformer_list[2][1]
        # جایگزینی کلاس با نمونه واقعی استخراج‌کننده
        model.named_steps['features'].transformer_list[2] = ('lexicon', lexicon_obj)
        
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
            print(f"{i}. Text: {text[:50]}... --> Prediction: {pred[0]}")
        except Exception as e:
            print(f"{i}. Text: {text[:50]}... --> Error: {e}")

if __name__ == "__main__":
    test_inference()
