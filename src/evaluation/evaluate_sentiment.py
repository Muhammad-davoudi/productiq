import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


@dataclass(frozen=True)
class RateMapping:
    neg_max: float = 2.0          # rate <= neg_max  -> 0
    pos_min: float = 4.0          # rate >= pos_min  -> 2


def map_rate_to_class(rate: float, mapping: RateMapping) -> int:
    # 0: negative, 1: neutral, 2: positive
    if rate <= mapping.neg_max:
        return 0
    if rate >= mapping.pos_min:
        return 2
    return 1


def load_dataset(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    # robust column handling
    expected = {"id", "text", "rate"}
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in {csv_path}: {sorted(missing)}")

    if df["text"].isna().any():
        raise ValueError("Found null texts in dataset.")
    if df["rate"].isna().any():
        raise ValueError("Found null rates in dataset.")

    return df


def evaluate(
    model_path: Path,
    csv_path: Path,
    mapping: RateMapping,
) -> Tuple[Dict, np.ndarray]:
    model = joblib.load(model_path)
    df = load_dataset(csv_path)

    y_true = df["rate"].astype(float).apply(lambda r: map_rate_to_class(r, mapping)).astype(int).to_numpy()
    y_pred = model.predict(df["text"].astype(str).to_list())

    labels = [0, 1, 2]
    metrics = {
        "model_path": str(model_path),
        "csv_path": str(csv_path),
        "mapping": {"neg_max": mapping.neg_max, "pos_min": mapping.pos_min},
        "n_rows": int(len(df)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=labels).tolist(),
        "classification_report": classification_report(
            y_true, y_pred, labels=labels, output_dict=True, zero_division=0
        ),
    }
    return metrics, y_pred


def main():
    parser = argparse.ArgumentParser(description="Evaluate baseline sentiment model on labeled CSV.")
    parser.add_argument("--csv", default="data/raw/labeling_sample_1200.csv", help="Path to labeled CSV.")
    parser.add_argument("--model", default="models/baseline_sentiment.joblib", help="Path to sentiment model joblib.")
    parser.add_argument("--out", default="reports/sentiment_eval_1200.json", help="Output JSON path.")
    parser.add_argument("--neg-max", type=float, default=2.0, help="Negative max threshold (rate <= neg_max).")
    parser.add_argument("--pos-min", type=float, default=4.0, help="Positive min threshold (rate >= pos_min).")
    args = parser.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    mapping = RateMapping(neg_max=args.neg_max, pos_min=args.pos_min)
    metrics, _ = evaluate(Path(args.model), Path(args.csv), mapping)

    out_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Wrote sentiment evaluation report to: {out_path}")
    print(f"Accuracy: {metrics['accuracy']:.4f}")


if __name__ == "__main__":
    main()
