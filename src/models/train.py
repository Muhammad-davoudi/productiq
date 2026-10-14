import os
import joblib
import pandas as pd
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import VotingClassifier
from sklearn.naive_bayes import MultinomialNB
from src.nlp.feature_engineering import PersianAdvancedFeatureExtractor

def build_sentiment_pipeline():
    features = FeatureUnion([
        ("word_tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=10000)),
        ("char_tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), max_features=10000)),
        ("lexicon", PersianAdvancedFeatureExtractor()),
    ])

    clf = VotingClassifier(
        estimators=[
            ("lr", LogisticRegression(max_iter=1000, random_state=42)),
            ("nb", MultinomialNB()),
        ],
        voting="soft"
    )

    pipeline = Pipeline([
        ("features", features),
        ("clf", clf),
    ])
    return pipeline

def train_and_save(data_path: str, model_output_path: str = "models/sentiment_model.pkl"):
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Training dataset not found: {data_path}")

    df = pd.read_csv(data_path)
    X = df["text"].astype(str)
    y = df["label"].astype(int)

    pipeline = build_sentiment_pipeline()
    pipeline.fit(X, y)

    os.makedirs(os.path.dirname(model_output_path), exist_ok=True)
    joblib.dump(pipeline, model_output_path)
    print(f"Sentiment pipeline model successfully saved to {model_output_path}")

if __name__ == "__main__":
    # Example invocation if run directly
    print("Sentiment pipeline training module ready.")
