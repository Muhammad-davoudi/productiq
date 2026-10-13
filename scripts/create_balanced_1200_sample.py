# -*- coding: utf-8 -*-
"""
Script to generate a balanced 1200-sample dataset (400 Positive, 400 Negative, 400 Neutral)
using the 3-class Digikala BERT model in src/nlp/sentiment.py.
Memory-safe with chunk-based reading for 8GB RAM environments.
"""

import os
import sys
import pandas as pd
from typing import Dict, List

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.nlp.sentiment import PersianSentimentAnalyzer

INPUT_CLEANED_COMMENTS = os.path.join(PROJECT_ROOT, "data/processed/cleaned_comments.csv")
RAW_OUTPUT_PATH = os.path.join(PROJECT_ROOT, "data/raw/labeling_sample_1200.csv")
LABELED_OUTPUT_PATH = os.path.join(PROJECT_ROOT, "data/processed/labeling_sample_1200_labeled.csv")

TARGET_PER_CLASS = 400
TARGET_CLASSES = {"Positive", "Negative", "Neutral"}


def sample_and_label():
    print("[INIT] Loading PersianSentimentAnalyzer...")
    analyzer = PersianSentimentAnalyzer()

    collected: Dict[str, List[dict]] = {
        "Positive": [],
        "Negative": [],
        "Neutral": []
    }

    print(f"[STREAM] Reading comments from: {INPUT_CLEANED_COMMENTS}")
    # چانک ۲۰۰۰تایی برای مصرف حافظه کمتر از ۱ گیگابایت در محیط ۸ گیگابایت
    chunk_size = 2000
    total_scanned = 0

    for chunk in pd.read_csv(INPUT_CLEANED_COMMENTS, chunksize=chunk_size, low_memory=False):
        # تطبیق نام ستون‌ها بر اساس هدر تأییدشده
        text_col = "body" if "body" in chunk.columns else ("text" if "text" in chunk.columns else "comment")
        id_col = "id" if "id" in chunk.columns else chunk.columns[0]
        rate_col = "rate" if "rate" in chunk.columns else None

        # فیلتر ردیف‌های نامعتبر یا خیلی کوتاه
        valid_rows = chunk[chunk[text_col].notna() & (chunk[text_col].astype(str).str.strip().str.len() > 10)]
        texts = valid_rows[text_col].astype(str).tolist()

        if not texts:
            continue

        results = analyzer.analyze_batch(texts, batch_size=32)
        total_scanned += len(texts)

        for (_, row), res in zip(valid_rows.iterrows(), results):
            label = res["sentiment"]
            conf = res["confidence"]

            if label in collected and len(collected[label]) < TARGET_PER_CLASS:
                collected[label].append({
                    "id": row[id_col],
                    "text": str(row[text_col]).strip(),
                    "rate": row[rate_col] if rate_col is not None else 0.0,
                    "sentiment_label": label,
                    "confidence": round(float(conf), 4),
                    "clean_sentiment": label
                })

        counts = {k: len(v) for k, v in collected.items()}
        print(f"[PROGRESS] Scanned: {total_scanned} | Counts: {counts}", end="\r")

        # توقف به‌محض تکمیل ۴۰۰تایی هر سه کلاس
        if all(len(v) >= TARGET_PER_CLASS for v in collected.values()):
            print("\n[SUCCESS] Reached 400 samples for all 3 classes!")
            break

    # ترکیب و ذخیره‌سازی داده‌ها
    all_samples = []
    for cls_name in ["Positive", "Negative", "Neutral"]:
        all_samples.extend(collected[cls_name][:TARGET_PER_CLASS])

    df_labeled = pd.DataFrame(all_samples)

    # ۱. ذخیره فایل خام ۱۲۰۰تایی در data/raw/labeling_sample_1200.csv
    df_raw = df_labeled[["id", "text", "rate"]]
    os.makedirs(os.path.dirname(RAW_OUTPUT_PATH), exist_ok=True)
    df_raw.to_csv(RAW_OUTPUT_PATH, index=False, encoding="utf-8-sig")
    print(f"\n[SAVED] Raw 1200 sample saved at: {RAW_OUTPUT_PATH}")

    # ۲. ذخیره فایل برچسب‌خورده ۱۲۰۰تایی در data/processed/labeling_sample_1200_labeled.csv
    os.makedirs(os.path.dirname(LABELED_OUTPUT_PATH), exist_ok=True)
    df_labeled.to_csv(LABELED_OUTPUT_PATH, index=False, encoding="utf-8-sig")
    print(f"[SAVED] Labeled 1200 sample saved at: {LABELED_OUTPUT_PATH}")

    print("\n--- Summary Distribution ---")
    print(df_labeled["sentiment_label"].value_counts())


if __name__ == "__main__":
    sample_and_label()
