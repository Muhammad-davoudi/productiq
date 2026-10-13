#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, f1_score, confusion_matrix

PROJECT_ROOT = Path(__file__).resolve().parents[1]
data_path = PROJECT_ROOT / "data/processed/labeling_sample_1000_labeled.csv"

df = pd.read_csv(data_path)

# فیلتر کردن صرفاً نظرات با قطبیت مشخص (حذف امتیاز ۳ یا خنثی‌های مبهم)
binary_df = df[df["clean_sentiment"].isin(["Positive", "Negative"])].copy()

print(f"Total samples for binary classification: {len(binary_df)}")
print(binary_df["clean_sentiment"].value_counts())

X = binary_df["text"].astype(str).values
y = binary_df["clean_sentiment"].astype(str).values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)),
    ("classifier", LogisticRegression(class_weight="balanced", random_state=42))
])

pipeline.fit(X_train, y_train)
y_pred = pipeline.predict(X_test)

acc = accuracy_score(y_test, y_pred)
macro_f1 = f1_score(y_test, y_pred, average="macro")

print("\n" + "="*50)
print("  BINARY BASELINE EVALUATION (Positive vs Negative)")
print("="*50)
print(f"Accuracy: {acc:.4f}")
print(f"Macro F1: {macro_f1:.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, digits=4))

print("Confusion Matrix:")
classes = sorted(list(set(y_test)))
cm = confusion_matrix(y_test, y_pred, labels=classes)
cm_df = pd.DataFrame(cm, index=[f"Actual {c}" for c in classes], columns=[f"Pred {c}" for c in classes])
print(cm_df)
