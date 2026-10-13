#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path
import pandas as pd
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.nlp.sentiment import PersianSentimentAnalyzer

def main():
    inp_path = PROJECT_ROOT / "data/raw/labeling_sample_1000.csv"
    out_path = PROJECT_ROOT / "data/processed/labeling_sample_1000_labeled.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if not inp_path.exists():
        print(f"Error: {inp_path} not found!")
        sys.exit(1)

    print(f"Reading sample from {inp_path}...")
    df = pd.read_csv(inp_path)

    text_col = "text" if "text" in df.columns else ("comment" if "comment" in df.columns else df.columns[0])
    print(f"Using text column: '{text_col}'")

    print("Initializing PersianSentimentAnalyzer (Singleton)...")
    analyzer = PersianSentimentAnalyzer()

    print(f"Labeling {len(df)} samples with Transformer & linguistic rules...")
    labels = []
    confidences = []

    for text in tqdm(df[text_col].astype(str), desc="Labeling Progress"):
        res = analyzer.analyze_sentence(text)
        # res returns a dict like {'label': '...', 'score': ...} or {'sentiment': '...', 'confidence': ...}
        if isinstance(res, dict):
            label = res.get("sentiment", res.get("label", "neutral"))
            score = res.get("confidence", res.get("score", 0.0))
        else:
            label = str(res)
            score = 1.0
        labels.append(label)
        confidences.append(score)

    df["sentiment_label"] = labels
    df["confidence"] = confidences

    df.to_csv(out_path, index=False, encoding="utf-8")
    print(f"\nLabeling completed successfully!")
    print(f"Saved labeled dataset to: {out_path}")
    print("\nLabel distribution:")
    print(df["sentiment_label"].value_counts())

if __name__ == "__main__":
    main()
