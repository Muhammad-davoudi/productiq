import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
from sklearn.metrics import accuracy_score, f1_score
from src.nlp.sentiment import BaselineSentimentModel, PersianSentimentAnalyzer

def evaluate_models():
    os.makedirs("data/processed", exist_ok=True)
    samples = [
        ("بسیار عالی و با کیفیت بود", "Positive"),
        ("راضی بودم و خریدش رو پیشنهاد میکنم", "Positive"),
        ("فوق العاده خوش دست و زیبا", "Positive"),
        ("افتضاحه، اصلا نخرید پشیمون میشید", "Negative"),
        ("خیلی بی کیفیته و زود خراب شد", "Negative"),
        ("بسته بندی داغون بود و مرجوع کردم", "Negative"),
        ("معمولی بود نه خیلی خوب نه خیلی بد", "Neutral"),
        ("یک محصول متوسط متناسب با قیمت", "Neutral")
    ]
    texts = [s[0] for s in samples]
    y_true = [s[1] for s in samples]

    # Baseline Model
    baseline = BaselineSentimentModel()
    baseline.fit(texts, y_true)
    preds_base = [p[0] for p in baseline.predict(texts)]

    # Transformer / Advanced Model
    analyzer = PersianSentimentAnalyzer()
    preds_trans = [analyzer.analyze_sentence(t)["sentiment"] for t in texts]

    report = {
        "baseline_ml": {
            "accuracy": float(accuracy_score(y_true, preds_base)),
            "macro_f1": float(f1_score(y_true, preds_base, average="macro", zero_division=0))
        },
        "transformer": {
            "accuracy": float(accuracy_score(y_true, preds_trans)),
            "macro_f1": float(f1_score(y_true, preds_trans, average="macro", zero_division=0))
        },
        "superior_model": "transformer" if f1_score(y_true, preds_trans, average="macro", zero_division=0) >= f1_score(y_true, preds_base, average="macro", zero_division=0) else "baseline_ml"
    }

    with open("data/processed/nlp_evaluation.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("Model Evaluation Results:")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    evaluate_models()
