#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, f1_score, confusion_matrix

PROJECT_ROOT = Path(__file__).resolve().parents[1]
data_path = PROJECT_ROOT / "data/processed/labeling_sample_1000_labeled.csv"
models_dir = PROJECT_ROOT / "models"
models_dir.mkdir(parents=True, exist_ok=True)
model_save_path = models_dir / "baseline_sentiment_svc.joblib"

if not data_path.exists():
    print(f"Error: {data_path} not found!")
    sys.exit(1)

print(f"Loading dataset from: {data_path}")
df = pd.read_csv(data_path)

# 1. برچسب‌گذاری دقیق و معتبر بر اساس امتیاز ۳ واقعی کاربر
def get_clean_label(row):
    rate = row.get("rate")
    if pd.notna(rate) and float(rate) == 3.0:
        return "Neutral"
    # در غیر این صورت، نظر مثبت یا منفی ترنسفورمر
    orig = str(row.get("sentiment_label", "")).strip()
    if orig in ["Positive", "Negative"]:
        return orig
    # اگر قبلا به اشتباه Neutral شده بود ولی امتیاز ۳ نبوده، بر اساس امتیاز تفکیک شود
    if pd.notna(rate) and float(rate) > 3.0:
        return "Positive"
    elif pd.notna(rate) and float(rate) < 3.0:
        return "Negative"
    return orig

df["clean_sentiment"] = df.apply(get_clean_label, axis=1)

print("\n--- Cleaned 3-Class Label Distribution ---")
print(df["clean_sentiment"].value_counts())
print("\nPercentages:")
print(df["clean_sentiment"].value_counts(normalize=True).round(3) * 100)

# ذخیره دیتاست تصحیح‌شده
df.to_csv(data_path, index=False, encoding="utf-8")

X = df["text"].astype(str).values
y = df["clean_sentiment"].astype(str).values

# 2. تفکیک لایه‌بندی‌شده داده‌ها به Train (80%) و Test (20%)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

print(f"\nDataset Split: Train = {len(X_train)} samples, Test = {len(X_test)} samples")

# 3. ساخت پایپ‌لاین پیشرفته TF-IDF + LinearSVC
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        ngram_range=(1, 3),
        min_df=2,
        max_df=0.9,
        sublinear_tf=True
    )),
    ("classifier", LinearSVC(
        C=1.0,
        class_weight="balanced",
        random_state=42,
        max_iter=3000
    ))
])

print("\nTraining LinearSVC Baseline model...")
pipeline.fit(X_train, y_train)

print("Evaluating on unseen test set...")
y_pred = pipeline.predict(X_test)

acc = accuracy_score(y_test, y_pred)
macro_f1 = f1_score(y_test, y_pred, average="macro")
weighted_f1 = f1_score(y_test, y_pred, average="weighted")

print("\n" + "="*55)
print("  LINEARSVC BASELINE EVALUATION RESULTS (Unseen Test)")
print("="*55)
print(f"Accuracy:    {acc:.4f}")
print(f"Macro F1:    {macro_f1:.4f}")
print(f"Weighted F1: {weighted_f1:.4f}")

print("\nDetailed Classification Report:")
print(classification_report(y_test, y_pred, digits=4))

print("Confusion Matrix:")
classes = sorted(list(set(y_test)))
cm = confusion_matrix(y_test, y_pred, labels=classes)
cm_df = pd.DataFrame(cm, index=[f"Actual {c}" for c in classes], columns=[f"Pred {c}" for c in classes])
print(cm_df)

# ذخیره پایپ‌لاین
joblib.dump(pipeline, model_save_path)
print(f"\nTrained model successfully saved to: {model_save_path}")
