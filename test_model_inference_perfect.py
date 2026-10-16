import sys
import inspect

if not hasattr(inspect, 'formatargspec'):
    def _formatargspec(args, varargs=None, varkwargs=None, defaults=None,
                       kwonlyargs=None, kwonlydefaults=None, annotations={},
                       formatvalue=lambda v: ""):
        return ""
    inspect.formatargspec = _formatargspec

import os
import joblib
import pandas as pd
import numpy as np

sys.path.append(os.getcwd())
from src.nlp.feature_engineering import PersianAdvancedFeatureExtractor

original_transform = PersianAdvancedFeatureExtractor.transform

def patched_transform(self, X):
    if isinstance(X, str):
        X = [X]
    base_features = original_transform(self, X)
    if not isinstance(base_features, np.ndarray):
        base_features = np.array(base_features)
    
    extra_list = []
    for text in X:
        if not isinstance(text, str):
            text = str(text) if text is not None else ""
        row = [
            float(len(text)),
            float(len(text.split())),
            float(text.count('!')),
            float(text.count('?')),
            float(sum(c.isdigit() for c in text)),
            float(sum(not c.isalnum() and not c.isspace() for c in text))
        ]
        extra_list.append(row)
    
    extra_arr = np.array(extra_list, dtype=np.float64)
    return np.hstack([base_features, extra_arr])

PersianAdvancedFeatureExtractor.transform = patched_transform

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
