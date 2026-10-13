#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, f1_score, confusion_matrix

PROJECT_ROOT = Path(__file__).resolve().parents[1]
data_path = PROJECT_ROOT / "data/processed/labeling_sample_1000_labeled.csv"
models_dir = PROJECT_ROOT / "models"
models_dir.mkdir(parents=True, exist_ok=True)
model_save_path = models_dir / "baseline_sentiment.joblib"

if not data_path.exists():
    print(f"Error: {data_path} not found!")
    sys.exit(1)

print(f"Loading ground-truth dataset from: {data_path}")
df = pd.read_csv(data_path)

# آماده‌سازی متن و برچسب
X = df["text"].astype(str).values
y = df["sentiment_label"].astype(str).values

# تقسیم داده به Train و Test (80/20) به صورت Stratified
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

print(f"Dataset split: Train={len(X_train)} samples, Test={len(X_test)} samples")

# ساخت خط‌لوله TF-IDF + Logistic Regression
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_features=5000
    )),
    ("classifier", LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=42
    ))
])

print("Training Baseline ML model...")
pipeline.fit(X_train, y_train)

print("Evaluating Baseline on unseen test data...")
y_pred = pipeline.predict(X_test)

acc = accuracy_score(y_test, y_pred)
macro_f1 = f1_score(y_test, y_pred, average="macro")

print("\n" + "="*50)
print("BASELINE ML EVALUATION RESULTS (Unseen Test Set)")
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

# ذخیره مدل
joblib.dump(pipeline, model_save_path)
print(f"\nTrained Baseline model saved to: {model_save_path}")
