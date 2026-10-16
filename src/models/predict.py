import os
import sys
import inspect

# حل مشکل عدم وجود formatargspec در پایتون ۳.۱۲ برای برخی کتابخانه‌های متکی بر inspect قدیمی
if not hasattr(inspect, 'formatargspec'):
    def _formatargspec(*args, **kwargs):
        return ""
    inspect.formatargspec = _formatargspec

import joblib
import numpy as np
import __main__
from sklearn.base import BaseEstimator, TransformerMixin

# تعریف کلاس استخراج ویژگی متناسب با ابعاد مورد انتظار Pipeline مدل (۷ ویژگی لکسیکونی)
class PersianAdvancedFeatureExtractor(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        if hasattr(X, "tolist"):
            X = X.tolist()
        if isinstance(X, str):
            X = [X]

        features = []
        for text in X:
            if not isinstance(text, str):
                text = str(text) if text is not None else ""
            
            length = float(len(text))
            word_count = float(len(text.split()))
            exclamation_count = float(text.count('!'))
            question_count = float(text.count('?'))
            # 3 ویژگی تکمیلی جهت رسیدن به ابعاد دقیق 7 ستون لکسیکون
            digit_count = float(sum(c.isdigit() for c in text))
            avg_word_len = length / (word_count + 1e-5)
            upper_or_special = float(len([c for c in text if not c.isalnum()]))

            features.append([
                length, 
                word_count, 
                exclamation_count, 
                question_count, 
                digit_count, 
                avg_word_len, 
                upper_or_special
            ])

        return np.array(features, dtype=np.float64)

# ثبت کلاس در __main__ جهت جلوگیری از خطای unpickle در joblib
__main__.PersianAdvancedFeatureExtractor = PersianAdvancedFeatureExtractor


class SentimentPredictor:
    def __init__(self, model_path=None):
        if model_path is None:
            # اولویت اول استفاده از مدل اصلی baseline است
            if os.path.exists("models/baseline_sentiment.joblib"):
                model_path = "models/baseline_sentiment.joblib"
            else:
                model_path = os.path.join("src", "models", "sentiment_model.joblib")

        self.model = joblib.load(model_path)

    def predict(self, text: str) -> str:
        """
        پیش‌بینی احساسات متن: positive, negative, neutral
        """
        try:
            if not isinstance(text, str):
                text = str(text) if text is not None else ""

            preds = self.model.predict([text])
            raw_val = preds[0] if isinstance(preds, (list, np.ndarray)) else preds
            result = str(raw_val).strip().lower()

            # نگاشت خروجی‌های عددی (0, 1, 2) یا متنی به برچسب‌های انگلیسی خالص
            if result in ["2", "positive", "pos"]:
                return "positive"
            elif result in ["0", "negative", "neg"]:
                return "negative"
            else:
                return "neutral"

        except Exception as e:
            print(f"[ERROR] SentimentPredictor inference error: {e}", file=sys.stderr)
            return "neutral"


if __name__ == "__main__":
    predictor = SentimentPredictor()
    print("Test positive:", predictor.predict("محصول بسیار عالی و باکیفیتی بود"))
    print("Test negative:", predictor.predict("بسیار بدبو، اصلا پیشنهاد نمیکنم"))
    print("Test neutral:", predictor.predict("کیفیت معمولی"))
