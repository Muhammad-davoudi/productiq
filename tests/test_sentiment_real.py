import os
import joblib
import unittest
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

# تعریف دقیق کلاس PersianAdvancedFeatureExtractor مطابق با train_and_compare_3class.py
class PersianAdvancedFeatureExtractor(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.pos_words = {
            "عالی", "خوب", "فوق‌العاده", "فوق العاده", "راضی", "عالیه", "خوبه",
            "کیفیت", "پیشنهاد", "مناسب", "کاربردی", "زیبا", "تمیز", "خوش‌دست",
            "سالم", "دوست‌داشتنی", "ارزش", "محکم", "شیک", "مرتب", "مطلوب", "عالییی"
        }
        self.neg_words = {
            "بد", "افتضاح", "خراب", "ناراضی", "حیف", "مرجوع", "نمی‌ارزه", "ضعیف",
            "کثیف", "سخت", "شکسته", "تقلبی", "گران", "گرون", "بی‌کیفیت", "ناامید",
            "نخرید", "اشتباه", "داغون", "پشیمان", "پشیمون", "کوچیک", "افتضاحه"
        }
        self.negation_words = {"نه", "نمی", "نیست", "نبود", "نشد", "اصلا", "هیچ", "بدون"}

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        features = []
        for text in X:
            if not isinstance(text, str):
                features.append([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
                continue
            words = text.split()
            n_words = max(len(words), 1)

            pos_cnt = sum(1 for w in words if any(pw in w for pw in self.pos_words))
            neg_cnt = sum(1 for w in words if any(nw in w for nw in self.neg_words))
            negate_cnt = sum(1 for w in words if any(nw in w for nw in self.negation_words))

            excl_count = text.count('!')
            quest_count = text.count('?')

            pos_ratio = pos_cnt / n_words
            neg_ratio = neg_cnt / n_words
            polarity_diff = (pos_cnt - neg_cnt) / (pos_cnt + neg_cnt + 1.0)

            features.append([pos_cnt, neg_cnt, pos_ratio, neg_ratio, polarity_diff, excl_count, quest_count])
        return np.array(features)

class TestSentimentModelReal(unittest.TestCase):
    
    def setUp(self):
        self.model_path = "models/baseline_sentiment.joblib"
        
    def test_sentiment_model_loading_and_prediction(self):
        print(f"\n[TEST] Checking sentiment model existence at: {self.model_path}")
        self.assertTrue(os.path.exists(self.model_path), f"Sentiment model not found at {self.model_path}")
        
        print("[TEST] Loading baseline sentiment model...")
        model = joblib.load(self.model_path)
        self.assertIsNotNone(model, "Loaded sentiment model is None")
        
        # نمونه متن‌های تستی برای ارزیابی احساسات (۳-کلاسه)
        test_samples = [
            "محصول فوق العاده ای است و ارزش خرید بالایی دارد.",
            "کیفیت معمولی داشت و نسبت به قیمت متوسط بود.",
            "اصلا راضی نیستم، خیلی زود خراب شد و کیفیت پایینی دارد."
        ]
        
        print("[TEST] Running predictions on sample texts...")
        predictions = model.predict(test_samples)
        print(f"Test samples and predictions: {list(zip(test_samples, predictions))}")
        
        self.assertEqual(len(predictions), len(test_samples))
        for text, pred in zip(test_samples, predictions):
            print(f"Text: '{text}' --> Predicted Sentiment: {pred}")

if __name__ == "__main__":
    unittest.main()
