#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report, accuracy_score, f1_score, confusion_matrix

PROJECT_ROOT = Path(__file__).resolve().parents[1]
data_path = PROJECT_ROOT / "data/processed/labeling_sample_1000_labeled.csv"

if not data_path.exists():
    print(f"File not found: {data_path}")
    sys.exit(1)

df = pd.read_csv(data_path)

# اطمینان از وجود ستون clean_sentiment
if "clean_sentiment" not in df.columns:
    def get_clean_label(row):
        rate = row.get("rate")
        if pd.notna(rate) and float(rate) == 3.0:
            return "Neutral"
        orig = str(row.get("sentiment_label", "")).strip()
        if orig in ["Positive", "Negative"]:
            return orig
        if pd.notna(rate) and float(rate) > 3.0:
            return "Positive"
        return "Negative"
    df["clean_sentiment"] = df.apply(get_clean_label, axis=1)

X = df["text"].astype(str).values
y = df["clean_sentiment"].astype(str).values

# تفکیک لایه‌بندی‌شده
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

print(f"Training set size: {len(X_train)} | Test set size: {len(X_test)}")
print("Train Class Distribution:\n", pd.Series(y_train).value_counts())

# ویژگی‌های ترکیبی: کلمات + قطعات کاراکتری (Subwords) برای پوشش پیشوندها و پسوندها
features = FeatureUnion([
    ("word_tfidf", TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        sublinear_tf=True
    )),
    ("char_tfidf", TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
        min_df=3,
        sublinear_tf=True
    ))
])

# وزن‌دهی دستی و تشدید وزن کلاس Neutral برای مقابله با عدم تعادل
# Negative: 1.0, Positive: 1.0, Neutral: 2.2
custom_weights = {"Negative": 1.0, "Neutral": 2.2, "Positive": 1.0}

pipe = Pipeline([
    ("features", features),
    ("clf", LinearSVC(class_weight=custom_weights, random_state=42, max_iter=4000))
])

# بهینه‌سازی پارامتر C با اعتبارسنجی متقاطع
param_grid = {
    "clf__C": [0.1, 0.3, 0.5, 0.8, 1.0, 1.5]
}

print("\nRunning Stratified GridSearchCV to tune LinearSVC...")
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
grid = GridSearchCV(pipe, param_grid, cv=cv, scoring="f1_macro", n_jobs=-1)
grid.fit(X_train, y_train)

best_model = grid.best_estimator_
print(f"Best Parameters: {grid.best_params_}")
print(f"Best CV Macro F1: {grid.best_score_:.4f}")

# ارزیابی روی داده‌های تست
y_pred = best_model.predict(X_test)

acc = accuracy_score(y_test, y_pred)
macro_f1 = f1_score(y_test, y_pred, average="macro")
weighted_f1 = f1_score(y_test, y_pred, average="weighted")

print("\n" + "="*55)
print("  TUNED 3-CLASS LINEARSVC EVALUATION RESULTS")
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
