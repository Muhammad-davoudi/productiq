from pathlib import Path
import json

from src.evaluation.evaluate_sentiment import RateMapping, evaluate


def test_phase_8_sentiment_evaluation_runs(tmp_path):
    model_path = Path("models/baseline_sentiment.joblib")
    csv_path = Path("data/raw/labeling_sample_1200.csv")

    assert model_path.exists(), "Sentiment model not found."
    assert csv_path.exists(), "Labeled sentiment CSV not found."

    mapping = RateMapping(neg_max=2.0, pos_min=4.0)
    metrics, _ = evaluate(model_path, csv_path, mapping)

    assert metrics["n_rows"] == 1200
    assert 0.0 <= metrics["accuracy"] <= 1.0

    cm = metrics["confusion_matrix"]
    assert isinstance(cm, list) and len(cm) == 3 and all(len(r) == 3 for r in cm)

    report = metrics["classification_report"]
    for k in ["0", "1", "2"]:
        assert k in report
        assert 0.0 <= report[k]["f1-score"] <= 1.0
