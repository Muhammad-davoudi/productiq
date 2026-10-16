import os
import joblib
import sys
import numpy as np

class PersianAdvancedFeatureExtractor:
    def __init__(self, *args, **kwargs):
        pass
    def fit(self, X, y=None):
        return self
    def transform(self, X):
        if isinstance(X, str):
            X = [X]
        # تست موقت برای بررسی ابعاد هر بخش
        return np.zeros((len(X), 4), dtype=np.float64)

setattr(sys.modules['__main__'], 'PersianAdvancedFeatureExtractor', PersianAdvancedFeatureExtractor)

model_path = os.path.join("models", "baseline_sentiment.joblib")
model = joblib.load(model_path)

print("Pipeline steps:")
for name, step in model.named_steps.items():
    print(f" - {name}: {type(step)}")
    if hasattr(step, 'transformer_list'):
        for t_name, t_obj in step.transformer_list:
            print(f"     * Sub-transformer {t_name}: {type(t_obj)}")

