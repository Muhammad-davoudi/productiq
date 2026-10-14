import os
import joblib
from typing import List, Union

class SentimentPredictor:
    def __init__(self, model_path: str = "models/baseline_sentiment.joblib"):
        # Fallback to alternative model path if default does not exist
        if not os.path.exists(model_path):
            alt_path = "models/sentiment_model.pkl"
            if os.path.exists(alt_path):
                model_path = alt_path

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}")

        self.model = joblib.load(model_path)

    def predict(self, texts: Union[str, List[str]]) -> List[int]:
        if isinstance(texts, str):
            texts = [texts]
        preds = self.model.predict(texts)
        return preds.tolist()

    def predict_proba(self, texts: Union[str, List[str]]):
        if isinstance(texts, str):
            texts = [texts]
        if hasattr(self.model, "predict_proba"):
            return self.model.predict_proba(texts)
        raise AttributeError("Underlying model does not support predict_proba")
