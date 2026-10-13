#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
file_path = PROJECT_ROOT / "data/processed/labeling_sample_1000_labeled.csv"

if not file_path.exists():
    print(f"Error: {file_path} not found!")
    sys.exit(1)

df = pd.read_csv(file_path)

def determine_sentiment(row):
    label = row["sentiment_label"]
    conf = float(row["confidence"])
    rate = float(row["rate"]) if pd.notna(row.get("rate")) else None

    # شرط ۱: مدل اطمینان پایینی دارد (بین مثبت و منفی مردد است)
    if conf < 0.70:
        return "Neutral"

    # شرط ۲: کاربر امتیاز ۳ داده و مدل اطمینان قطعی و قاطع (> 0.90) ندارد
    if rate == 3 and conf < 0.90:
        return "Neutral"

    # در بقیه حالات، برچسب مدل معتبر است
    return label

df["sentiment_label"] = df.apply(determine_sentiment, axis=1)

df.to_csv(file_path, index=False, encoding="utf-8")
print("Refined labeling completed successfully!")
print(f"File updated: {file_path}\n")
print("New 3-class distribution:")
print(df["sentiment_label"].value_counts())
print("\nPercentage distribution:")
print(df["sentiment_label"].value_counts(normalize=True).round(3) * 100)
