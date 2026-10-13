#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path
import torch
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, f1_score, confusion_matrix
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

data_path = PROJECT_ROOT / "data/processed/labeling_sample_1000_labeled.csv"
df = pd.read_csv(data_path)

X = df["text"].astype(str).values
y = df["clean_sentiment"].astype(str).values

_, X_test, _, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

MODEL_NAME = "HooshvareLab/bert-fa-base-uncased-sentiment-digikala"
print(f"Loading cached {MODEL_NAME} on CPU...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
model.eval()

# نگاشت قطعی بر اساس دیکشنری مدل:
# 0 -> no_idea -> Neutral
# 1 -> not_recommended -> Negative
# 2 -> recommended -> Positive
INDEX_TO_SENTIMENT = {
    0: "Neutral",
    1: "Negative",
    2: "Positive"
}

preds = []
print(f"Evaluating {len(X_test)} unseen test samples...")

with torch.no_grad():
    for text in tqdm(X_test, desc="Inference"):
        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=128,
            padding=False
        )
        outputs = model(**inputs)
        pred_id = torch.argmax(outputs.logits, dim=1).item()
        preds.append(INDEX_TO_SENTIMENT.get(pred_id, "Neutral"))

acc = accuracy_score(y_test, preds)
macro_f1 = f1_score(y_test, preds, average="macro")
weighted_f1 = f1_score(y_test, preds, average="weighted")

print("\n" + "="*55)
print("  HOOSHVARE DIGIKALA BERT (CORRECT MAPPING)")
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
