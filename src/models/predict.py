import os
import numpy as np
import joblib

class SentimentPredictor:
    def __init__(self, model_path=None):
        if model_path is None:
            candidates = [
                "models/sentiment_model.joblib",
                "/app/models/sentiment_model.joblib",
                "backup/sentiment/models/baseline_sentiment_svc.joblib",
                "/app/backup/sentiment/models/baseline_sentiment_svc.joblib",
            ]
            for p in candidates:
                if os.path.exists(p):
                    model_path = p
                    break

        if not model_path or not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found. Candidates: {candidates}")

        self.model_path = model_path
        self.model = joblib.load(model_path)
        print(f"[INFO] SentimentPredictor loaded model from: {model_path}")

    def predict(self, text: str) -> str:
        if not isinstance(text, str):
            text = str(text) if text is not None else ""

        # فقط اجرای مستقیم مدل یادگیری ماشین، بدون هاردکد، بدون کی‌ورد و بدون مپینگ دستی
        preds = self.model.predict([text])
        raw_val = preds[0] if isinstance(preds, (list, np.ndarray)) else preds

        # استانداردسازی شکل حروف (Positive -> positive)
        label = str(raw_val).strip().lower()
        if label in ("positive", "negative", "neutral"):
            return label

        raise ValueError(f"Unexpected raw model prediction: {raw_val}")
