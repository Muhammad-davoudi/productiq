import pandas as pd

FEATURE_MATRIX_PATH = "data/processed/product_feature_matrix.csv"
CLUSTERS_PATH = "data/processed/product_clusters.csv"

def debug():
    df_features = pd.read_csv(FEATURE_MATRIX_PATH)
    df_clusters = pd.read_csv(CLUSTERS_PATH)
    
    # Clean whitespace just in case
    df_features.columns = df_features.columns.str.strip()
    df_clusters.columns = df_clusters.columns.str.strip()

    print(f"Features columns: {df_features.columns.tolist()}")
    print(f"Clusters columns: {df_clusters.columns.tolist()}")
    
    # Merge
    df = pd.merge(df_features, df_clusters, on='product_id')
    print(f"Merged columns: {df.columns.tolist()}")
    print("-" * 20)
    print("Data types of relevant columns:")
    test_cols = ['price', 'rate', 'review_count', 'positive_ratio', 'recommendation_ratio']
    for col in test_cols:
        if col in df.columns:
            print(f"{col}: {df[col].dtype}")
        else:
            print(f"{col}: MISSING")

if __name__ == "__main__":
    debug()
