"""
Phase 3 - Product Feature Engineering
Builds the Product Feature Matrix from Phase 1 cleaned data
and Phase 2 NLP outputs, then validates it.
"""
import os
import json
import numpy as np
import pandas as pd

DATA_DIR = "data/processed"
OUTPUT_PATH = os.path.join(DATA_DIR, "product_feature_matrix.csv")

RATIO_COLS = [
    "positive_ratio", "negative_ratio", "neutral_ratio",
    "conflicted_ratio", "recommendation_ratio",
]

RECOMMENDED = "recommended"
NOT_RECOMMENDED = "not_recommended"


def load_phase_outputs():
    """Load Phase 1 cleaned data and Phase 2 NLP outputs."""
    products = pd.read_csv(os.path.join(DATA_DIR, "cleaned_products.csv"))
    comments = pd.read_csv(os.path.join(DATA_DIR, "cleaned_comments.csv"),
                           usecols=["id", "product_id", "rate", "recommendation_status"])
    nlp_reviews = pd.read_csv(os.path.join(DATA_DIR, "nlp_reviews.csv"))
    nlp_aggregated = pd.read_csv(os.path.join(DATA_DIR, "nlp_products_aggregated.csv"))
    return products, comments, nlp_reviews, nlp_aggregated


def validate_keys(products, comments, nlp_reviews, nlp_aggregated):
    """Validate product_id presence, types, nulls, duplicates and cardinality."""
    report = {
        "products_ids": int(products["id"].nunique()),
        "products_duplicate_ids": int(products["id"].duplicated().sum()),
        "products_null_ids": int(products["id"].isna().sum()),
        "comments_null_product_id": int(comments["product_id"].isna().sum()),
        "nlp_reviews_null_product_id": int(nlp_reviews["product_id"].isna().sum()),
    }

    product_ids = set(products["id"].dropna().astype(int))
    comment_ids = comments["product_id"].dropna().astype(int)
    report["comments_unknown_product_id"] = int((~comment_ids.isin(product_ids)).sum())

    report["nlp_reviews_duplicate_review_id"] = int(nlp_reviews["review_id"].duplicated().sum())
    report["nlp_aggregated_duplicate_product_id"] = int(nlp_aggregated["product_id"].duplicated().sum())

    print(json.dumps(report, indent=2, ensure_ascii=False))
    return report


def build_review_level_features(comments, nlp_reviews):
    """
    Merge review-level sentiment (Phase 2) with review metadata (Phase 1),
    then aggregate per product.
    """
    reviews = nlp_reviews.merge(
        comments.rename(columns={"id": "review_id"})[
            ["review_id", "product_id", "rate", "recommendation_status"]
        ],
        on=["review_id", "product_id"],
        how="inner",
        validate="one_to_one",
    )

    reviews["valid_rate"] = reviews["rate"].where(reviews["rate"] > 0)

    reviews["is_positive"] = reviews["overall_sentiment"].isin(
        ["Positive", "Mostly Positive"])
    reviews["is_negative"] = reviews["overall_sentiment"].isin(
        ["Negative", "Mostly Negative"])
    reviews["is_neutral"] = reviews["overall_sentiment"] == "Neutral"
    reviews["is_conflicted"] = reviews["overall_sentiment"] == "Conflicted"
    reviews["is_recommended"] = reviews["recommendation_status"] == RECOMMENDED
    reviews["has_rec_status"] = reviews["recommendation_status"].isin(
        [RECOMMENDED, NOT_RECOMMENDED])

    grouped = reviews.groupby("product_id").agg(
        review_count=("review_id", "count"),
        average_review_rating=("valid_rate", "mean"),
        positive_sum=("is_positive", "sum"),
        negative_sum=("is_negative", "sum"),
        neutral_sum=("is_neutral", "sum"),
        conflicted_sum=("is_conflicted", "sum"),
        recommended_sum=("is_recommended", "sum"),
        has_rec_sum=("has_rec_status", "sum"),
        average_sentiment_score=("dominant_sentiment", "count"),
    ).reset_index()

    score_map = reviews.groupby("product_id")["sentiment_score"] \
        .mean() if "sentiment_score" in reviews.columns else None
    if score_map is not None:
        grouped["average_sentiment_score"] = grouped["product_id"].map(score_map)
    else:
        grouped["average_sentiment_score"] = 0.0

    total = grouped["review_count"].replace(0, np.nan)
    for col, src in [("positive_ratio", "positive_sum"),
                     ("negative_ratio", "negative_sum"),
                     ("neutral_ratio", "neutral_sum"),
                     ("conflicted_ratio", "conflicted_sum")]:
        grouped[col] = (grouped[src] / total).fillna(0.0)

    rec_den = grouped["has_rec_sum"].replace(0, np.nan)
    grouped["recommendation_ratio"] = (grouped["recommended_sum"] / rec_den).fillna(0.0)

    grouped = grouped.drop(
        columns=["positive_sum", "negative_sum", "neutral_sum",
                 "conflicted_sum", "recommended_sum", "has_rec_sum"])

    return grouped


def build_product_feature_matrix():
    """Full Phase 3 pipeline: load -> validate -> merge -> engineer -> validate -> save."""
    products, comments, nlp_reviews, nlp_aggregated = load_phase_outputs()

    validate_keys(products, comments, nlp_reviews, nlp_aggregated)

    base = products.rename(columns={
        "id": "product_id", "Rate": "rate", "Rate_cnt": "rate_cnt",
        "Category1": "category", "Category2": "subcategory",
        "Brand": "brand", "Seller": "seller", "Is_Fake": "is_fake",
        "Price": "price"
    })[["product_id", "price", "rate", "rate_cnt", "category",
        "subcategory", "brand", "seller", "is_fake"]]

    review_feats = build_review_level_features(comments, nlp_reviews)

    matrix = base.merge(review_feats, on="product_id", how="left", validate="one_to_one")

    matrix["review_count"] = matrix["review_count"].fillna(0).astype(int)
    for col in RATIO_COLS + ["average_review_rating", "average_sentiment_score"]:
        matrix[col] = matrix[col].fillna(0.0)

    matrix = validate_features(matrix)

    matrix.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved feature matrix: {OUTPUT_PATH} | rows={len(matrix)}")
    return matrix


def validate_features(matrix):
    """Feature validation: ranges, ratios, counts, missing values."""
    issues = {}

    dup = matrix["product_id"].duplicated().sum()
    if dup:
        issues["duplicate_product_id"] = int(dup)

    if (matrix["price"] < 0).any():
        issues["negative_price"] = int((matrix["price"] < 0).sum())
    if (matrix["rate_cnt"] < 0).any():
        issues["negative_rate_cnt"] = int((matrix["rate_cnt"] < 0).sum())
    if (matrix["review_count"] < 0).any():
        issues["negative_review_count"] = int((matrix["review_count"] < 0).sum())

    for col in RATIO_COLS:
        out = ((matrix[col] < 0) | (matrix[col] > 1)).sum()
        if out:
            issues[f"{col}_out_of_range"] = int(out)

    bad_rate = ((matrix["rate"] < 0) | (matrix["rate"] > 5)).sum()
    if bad_rate:
        issues["rate_out_of_range"] = int(bad_rate)

    missing = matrix.isna().sum()
    issues["missing_values"] = {k: int(v) for k, v in missing.items() if v > 0}

    if issues:
        print("Validation issues:")
        print(json.dumps(issues, indent=2, ensure_ascii=False))
    else:
        print("Feature validation passed with no issues.")

    return matrix


if __name__ == "__main__":
    build_product_feature_matrix()
