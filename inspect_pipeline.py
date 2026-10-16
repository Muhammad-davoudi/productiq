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
        return np.zeros((len(X), 1)) # موقتاً برای تست ابعاد

setattr(sys.modules['__main__'], 'PersianAdvancedFeatureExtractor', PersianAdvancedFeatureExtractor)

model = joblib.load("models/baseline_sentiment.joblib")
print("Pipeline steps:")
for name, step in model.steps:
    print(f" - {name}: {type(step)}")
    if hasattr(step, "transformer_list"):
        for t_name, t_obj in step.transformer_list:
            print(f"    * Sub-transformer {t_name}: {type(t_obj)}")
