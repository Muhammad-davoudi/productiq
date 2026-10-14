import re
import hazm
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

class SentimentLexiconFeaturizer:
    def __init__(self):
        self.normalizer = hazm.Normalizer()
    def fit(self, X, y=None):
        return self
    def transform(self, texts):
        # Return numeric features array/matrix for pipeline hstack
        return np.array([[len(str(t))] for t in texts], dtype=float)

class UnifiedFeatureExtractor:
    def __init__(self):
        self.normalizer = hazm.Normalizer()
    def extract(self, text):
        return [len(str(text))]
    def get_features(self, text):
        # Return numeric feature vector for single item inference
        return np.array([[len(str(text))]], dtype=float)

class PersianAdvancedFeatureExtractor(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.extractor = UnifiedFeatureExtractor()
    def fit(self, X, y=None):
        return self
    def transform(self, X):
        if hasattr(X, "tolist"):
            X = X.tolist()
        if isinstance(X, str):
            X = [X]
        return np.array([[len(str(text))] for text in X], dtype=float)
