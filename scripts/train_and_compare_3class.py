import os
import re
import joblib
import numpy as np
import pandas as pd
from hazm import Normalizer
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import VotingClassifier
from sklearn.metrics import classification_report, accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import FeatureUnion, Pipeline

print("1. Loading Hazm Normalizer...")
normalizer = Normalizer()

def advanced_normalize(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = normalizer.normalize(text)
    text = re.sub(r'[^\w\s\!\?]', ' ', text)
    return re.sub(r'[\r\n\t]+', ' ', text).strip()

from src.nlp.feature_engineering import PersianAdvancedFeatureExtractor
from src.nlp.feature_engineering import PersianAdvancedFeatureExtractor
def map_rate_to_label(rate):
    try:
        r = float(rate)
        if r <= 2.0:
            return 0  # Negative
        elif r == 3.0:
            return 1  # Neutral
        else:
            return 2  # Positive
    except Exception:
        return -1

def main():
    csv_path = "data/raw/labeling_sample_1200.csv"
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    df = pd.read_csv(csv_path)
    df = df.dropna(subset=["text", "rate"])
    df["label"] = df["rate"].apply(map_rate_to_label)
    df = df[df["label"] != -1].reset_index(drop=True)

    print(f"Dataset Size: {len(df)}")
    print("Class counts:\n", df["label"].value_counts().sort_index())

    df["clean_text"] = df["text"].apply(advanced_normalize)

    X = df["clean_text"].values
    y = df["label"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    print("\n3. Building State-of-the-Art Ensemble Pipeline...")
    
    # Feature Extractor Pipeline
    feature_union = FeatureUnion([
        ("word_tfidf", TfidfVectorizer(
            ngram_range=(1, 3),
            min_df=2,
            max_df=0.95,
            sublinear_tf=True
        )),
        ("char_tfidf", TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            min_df=2,
            max_df=0.95,
            sublinear_tf=True
        )),
        ("lexicon", PersianAdvancedFeatureExtractor())
    ])

    # Ensemble Classifier (LinearSVC + LogisticRegression)
    svm_clf = CalibratedClassifierCV(LinearSVC(C=1.5, class_weight='balanced', random_state=42, max_iter=2000))
    lr_clf = LogisticRegression(C=3.0, class_weight='balanced', max_iter=2000, random_state=42)

    voting_clf = VotingClassifier(
        estimators=[('svm', svm_clf), ('lr', lr_clf)],
        voting='soft',
        weights=[1.5, 1.0]
    )

    pipeline = Pipeline([
        ("features", feature_union),
        ("clf", voting_clf)
    ])

    print("4. Training Ensemble Model...")
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average="macro")

    print("\n==================================================")
    print("ENSEMBLE TEST SET EVALUATION (20% Holdout):")
    print("==================================================")
    target_names = ["Negative (0)", "Neutral (1)", "Positive (2)"]
    print(classification_report(y_test, y_pred, target_names=target_names, digits=2))
    print(f"Final Test Macro F1: {macro_f1:.4f}")
    print(f"Final Test Accuracy: {acc:.4f}")

    os.makedirs("models", exist_ok=True)
    out_model_path = "models/baseline_sentiment.joblib"
    joblib.dump(pipeline, out_model_path)
    print(f"\nSaved ensemble pipeline to {out_model_path}")

if __name__ == "__main__":
    main()
