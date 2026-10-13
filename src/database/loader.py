"""
Phase 3/4 - Database Loader
Creates database schema and loads processed data (Products, Product Features, Product Clusters)
into PostgreSQL in batches to stay within 8GB RAM constraints.
"""
import os
import pandas as pd
from src.database.connection import engine, SessionLocal
from src.database.models import Base, Product, ProductFeature, ProductCluster

BATCH_SIZE = 10000


def init_db():
    """Create all defined tables if they do not exist."""
    Base.metadata.create_all(bind=engine)
    print("Database tables verified/created successfully.")


def load_products_and_features(matrix_path="data/processed/product_feature_matrix.csv"):
    """
    Load product_feature_matrix into PostgreSQL products and product_features tables.
    Processes in chunks to preserve memory.
    """
    if not os.path.exists(matrix_path):
        raise FileNotFoundError(f"Feature matrix file not found: {matrix_path}")

    init_db()
    session = SessionLocal()

    print(f"Loading data from {matrix_path} in chunks of {BATCH_SIZE}...")

    total_loaded = 0
    chunk_iter = pd.read_csv(matrix_path, chunksize=BATCH_SIZE)

    try:
        for i, chunk in enumerate(chunk_iter):
            products_records = []
            features_records = []

            for _, row in chunk.iterrows():
                p_id = int(row["product_id"])
                is_fake = bool(row["is_fake"]) if pd.notna(row["is_fake"]) else False

                products_records.append({
                    "id": p_id,
                    "price": float(row["price"]) if pd.notna(row["price"]) else 0.0,
                    "rate": float(row["rate"]) if pd.notna(row["rate"]) else 0.0,
                    "rate_cnt": int(row["rate_cnt"]) if pd.notna(row["rate_cnt"]) else 0,
                    "category1": str(row["category"]) if pd.notna(row["category"]) else None,
                    "category2": str(row["subcategory"]) if pd.notna(row["subcategory"]) else None,
                    "brand": str(row["brand"]) if pd.notna(row["brand"]) else None,
                    "seller": str(row["seller"]) if pd.notna(row["seller"]) else None,
                    "is_fake": is_fake,
                })

                features_records.append({
                    "product_id": p_id,
                    "price": float(row["price"]) if pd.notna(row["price"]) else 0.0,
                    "rate": float(row["rate"]) if pd.notna(row["rate"]) else 0.0,
                    "rate_cnt": int(row["rate_cnt"]) if pd.notna(row["rate_cnt"]) else 0,
                    "category": str(row["category"]) if pd.notna(row["category"]) else None,
                    "subcategory": str(row["subcategory"]) if pd.notna(row["subcategory"]) else None,
                    "brand": str(row["brand"]) if pd.notna(row["brand"]) else None,
                    "seller": str(row["seller"]) if pd.notna(row["seller"]) else None,
                    "is_fake": is_fake,
                    "review_count": int(row["review_count"]) if pd.notna(row["review_count"]) else 0,
                    "positive_ratio": float(row["positive_ratio"]) if pd.notna(row["positive_ratio"]) else 0.0,
                    "negative_ratio": float(row["negative_ratio"]) if pd.notna(row["negative_ratio"]) else 0.0,
                    "neutral_ratio": float(row["neutral_ratio"]) if pd.notna(row["neutral_ratio"]) else 0.0,
                    "conflicted_ratio": float(row["conflicted_ratio"]) if pd.notna(row["conflicted_ratio"]) else 0.0,
                    "recommendation_ratio": float(row["recommendation_ratio"]) if pd.notna(row["recommendation_ratio"]) else 0.0,
                    "average_review_rating": float(row["average_review_rating"]) if pd.notna(row["average_review_rating"]) else 0.0,
                    "average_sentiment_score": float(row["average_sentiment_score"]) if pd.notna(row["average_sentiment_score"]) else 0.0,
                })

            session.bulk_insert_mappings(Product, products_records)
            session.bulk_insert_mappings(ProductFeature, features_records)
            session.commit()

            total_loaded += len(chunk)
            print(f"Batch {i + 1} processed: {total_loaded} records inserted.")

        print(f"Completed! Total loaded records: {total_loaded}")

    except Exception as e:
        session.rollback()
        print(f"Error during loading: {e}")
        raise e
    finally:
        session.close()


def load_product_clusters(clusters_df_or_path="data/processed/product_clusters.csv"):
    """Load cluster assignments into PostgreSQL product_clusters table."""
    if isinstance(clusters_df_or_path, str):
        if not os.path.exists(clusters_df_or_path):
            raise FileNotFoundError(f"Cluster assignments file not found: {clusters_df_or_path}")
        df = pd.read_csv(clusters_df_or_path)
    else:
        df = clusters_df_or_path

    init_db()
    session = SessionLocal()

    print(f"Loading {len(df)} cluster assignments into database...")
    try:
        # Clear existing clusters if re-running
        session.query(ProductCluster).delete()
        session.commit()

        records = [
            {"product_id": int(r["product_id"]), "cluster_id": int(r["cluster_id"])}
            for _, r in df[["product_id", "cluster_id"]].iterrows()
        ]

        # Insert in chunks to avoid memory spikes
        for i in range(0, len(records), BATCH_SIZE):
            chunk = records[i:i + BATCH_SIZE]
            session.bulk_insert_mappings(ProductCluster, chunk)
            session.commit()

        print(f"Successfully loaded {len(records)} product clusters into PostgreSQL.")
    except Exception as e:
        session.rollback()
        print(f"Error loading clusters: {e}")
        raise e
    finally:
        session.close()


if __name__ == "__main__":
    load_products_and_features()
