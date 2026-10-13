import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from typing import Dict, List
from src.nlp.sentence_splitter import PersianSentenceSplitter
from src.nlp.sentiment import PersianSentimentAnalyzer
from src.nlp.aspect_extraction import AspectExtractor
from src.nlp.aspect_sentiment import AspectSentimentAnalyzer
from src.nlp.review_sentiment import ReviewSentimentEngine

def aggregate_product_insights(reviews_df: pd.DataFrame, aspects_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregates review & aspect metrics per product_id."""
    if reviews_df.empty or "product_id" not in reviews_df.columns:
        return pd.DataFrame()

    records = []
    grouped = reviews_df.groupby("product_id")
    
    for product_id, group in grouped:
        total = len(group)
        pos_ratio = (group["overall_sentiment"].isin(["Positive", "Mostly Positive"])).sum() / total
        neg_ratio = (group["overall_sentiment"].isin(["Negative", "Mostly Negative"])).sum() / total
        neu_ratio = (group["overall_sentiment"] == "Neutral").sum() / total
        conf_ratio = (group["overall_sentiment"] == "Conflicted").sum() / total
        avg_score = group["confidence"].mean()

        records.append({
            "product_id": product_id,
            "total_reviews": total,
            "positive_ratio": round(pos_ratio, 4),
            "negative_ratio": round(neg_ratio, 4),
            "neutral_ratio": round(neu_ratio, 4),
            "conflicted_ratio": round(conf_ratio, 4),
            "average_sentiment_score": round(avg_score, 4)
        })

    return pd.DataFrame(records)

def process_batch(df_chunk: pd.DataFrame, splitter, sent_analyzer, aspect_extractor, aspect_sent_analyzer, review_engine):
    sentences_records = []
    aspects_records = []
    reviews_records = []

    for _, row in df_chunk.iterrows():
        review_id = row.get("id", row.get("comment_id", _))
        product_id = row.get("product_id", None)
        text = str(row.get("comment_text", row.get("body", "")))

        sentences = splitter.split(text)
        s_evals = []

        for s_idx, sentence in enumerate(sentences):
            s_res = sent_analyzer.analyze_sentence(sentence)
            s_evals.append(s_res)
            sentences_records.append({
                "review_id": review_id,
                "sentence_id": f"{review_id}_{s_idx}",
                "sentence": sentence,
                "sentiment": s_res["sentiment"],
                "sentiment_score": s_res["sentiment_score"]
            })

            found_aspects = aspect_extractor.extract_aspects(sentence)
            asp_evals = aspect_sent_analyzer.analyze_aspects_in_sentence(sentence, found_aspects)
            for asp in asp_evals:
                aspects_records.append({
                    "review_id": review_id,
                    "sentence_id": f"{review_id}_{s_idx}",
                    "aspect": asp["aspect"],
                    "aspect_sentiment": asp["aspect_sentiment"],
                    "aspect_score": asp["aspect_score"]
                })

        rev_dec = review_engine.evaluate(s_evals)
        reviews_records.append({
            "review_id": review_id,
            "product_id": product_id,
            "overall_sentiment": rev_dec["overall_sentiment"],
            "dominant_sentiment": rev_dec["dominant_sentiment"],
            "confidence": rev_dec["confidence"],
            "conflict_score": rev_dec["conflict_score"]
        })

    return pd.DataFrame(sentences_records), pd.DataFrame(aspects_records), pd.DataFrame(reviews_records)

if __name__ == "__main__":
    comments_file = "data/raw/digikala-comments.csv"
    os.makedirs("data/processed", exist_ok=True)
    
    splitter = PersianSentenceSplitter()
    sent_analyzer = PersianSentimentAnalyzer()
    aspect_extractor = AspectExtractor()
    aspect_sent_analyzer = AspectSentimentAnalyzer(sent_analyzer)
    review_engine = ReviewSentimentEngine()

    print("Running NLP Pipeline in manageable chunks...")
    if os.path.exists(comments_file):
        sample_chunk = pd.read_csv(comments_file, nrows=1000)
    else:
        sample_chunk = pd.DataFrame([
            {"id": 1, "product_id": 101, "comment_text": "دوربین خیلی خوبه ولی باتری ضعیفه."},
            {"id": 2, "product_id": 101, "comment_text": "طراحی گوشی هم قشنگه و قیمت مناسبی داره."},
            {"id": 3, "product_id": 102, "comment_text": "اصلا راضی نیستم، کیفیت ساخت افتضاح بود."}
        ])

    df_sent, df_asp, df_rev = process_batch(sample_chunk, splitter, sent_analyzer, aspect_extractor, aspect_sent_analyzer, review_engine)
    df_prod = aggregate_product_insights(df_rev, df_asp)

    df_sent.to_csv("data/processed/nlp_sentences.csv", index=False)
    df_asp.to_csv("data/processed/nlp_aspects.csv", index=False)
    df_rev.to_csv("data/processed/nlp_reviews.csv", index=False)
    df_prod.to_csv("data/processed/nlp_products_aggregated.csv", index=False)
    print("NLP Processing complete. Artifacts saved in data/processed/")
