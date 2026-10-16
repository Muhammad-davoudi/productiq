import joblib
import numpy as np
import sys

class PersianAdvancedFeatureExtractor:
    def __init__(self, *args, **kwargs):
        pass
    def fit(self, X, y=None):
        return self
    def transform(self, X):
        if isinstance(X, str):
            X = [X]
        return np.zeros((len(X), 3)) # آزمایش با 3 ویژگی

setattr(sys.modules['__main__'], 'PersianAdvancedFeatureExtractor', PersianAdvancedFeatureExtractor)

model = joblib.load("models/baseline_sentiment.joblib")
lexicon_step = model.named_steps['features'].transformer_list[2][1]
print("Lexicon step object:", type(lexicon_step))
# بررسی ویژگی‌های داخلی شیء lexicon اگر ذخیره شده باشد
print(dir(lexicon_step))
