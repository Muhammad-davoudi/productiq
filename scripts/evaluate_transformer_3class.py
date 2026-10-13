#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import re
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, f1_score, confusion_matrix
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.nlp.sentiment import PersianSentimentAnalyzer

data_path = PROJECT_ROOT / "data/processed/labeling_sample_1000_labeled.csv"
df = pd.read_csv(data_path)

X = df["text"].astype(str).values
y = df["clean_sentiment"].astype(str).values

_, X_test, _, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

analyzer = PersianSentimentAnalyzer()

# الگوهای قطعی خنثی یا تضاد در زبان فارسی (مطابق بخش 14 سند A.txt)
NEUTRAL_PATTERNS = [
    r"\bمعمولی\b",
    r"\bبد نیست\b",
    r"\bمتوسط\b",
    r"\bدر حد خودش\b",
    r"\bنسبتا\b",
    r"\bکار راه انداز\b",
    r"\bارزش خرید متوسط\b"
]
neutral_regex = re.compile("|".join(NEUTRAL_PATTERNS))

preds = []
for text in tqdm(X_test, desc="Evaluating"):
    # 1. آیا الگوی صریح خنثی در متن وجود دارد؟
    if neutral_regex.search(text):
        preds.append("Neutral")
        continue

    # 2. ارزیابی مدل عمیق ترنسفورمر
    res = analyzer.analyze_sentence(text)
    sentiment = res.get("sentiment", "Neutral")
    conf = res.get("confidence", 0.5)

    # 3. اگر اطمینان مدل در ناحیه خاکستری باشد (< 0.82)
    if conf < 0.82:
        preds.append("Neutral")
    else:
        preds.append(sentiment)

acc = accuracy_score(y_test, preds)
macro_f1 = f1_score(y_test, preds, average="macro")
weighted_f1 = f1_score(y_test, preds, average="weighted")

print("\n" + "="*55)
print("  REFINED TRANSFORMER 3-CLASS EVALUATION")
print("="*55)
print(f"Accuracy:    {acc:.4f}")
print(f"Macro F1:    {macro_f1:.4f}")
print(f"Weighted F1: {weighted_f1:.4f}")

print("\nDetailed Classification Report:")
print(classification_report(y_test, preds, digits=4))

print("Confusion Matrix:")
classes = sorted(list(set(y_test)))
cm = confusion_matrix(y_test, preds, labels=classes)
cm_df = pd.DataFrame(cm, index=[f"Actual {c}" for c in classes], columns=[f"Pred {c}" for c in classes])
print(cm_df)
