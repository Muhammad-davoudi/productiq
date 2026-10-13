import pandas as pd
import numpy as np
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def evaluate_clustering():
    print("\n--- Evaluating Clustering (Safe Sampling Mode - 10k Samples) ---")
    
    df_features = pd.read_csv('data/processed/product_feature_matrix.csv')
    df_clusters = pd.read_csv('data/processed/product_clusters.csv')

    # ترکیب داده‌ها برای نمونه‌برداری
    df = pd.concat([df_features, df_clusters['cluster']], axis=1)
    
    # نمونه‌برداری ایمن (۱۰ هزار ردیف کافیست)
    sample_size = min(10000, len(df))
    df_sample = df.sample(n=sample_size, random_state=42)

    features = df_sample.drop(columns=['cluster']).select_dtypes(include=[np.number]).values
    clusters = df_sample['cluster'].values

    # Scaling & PCA
    features_scaled = StandardScaler().fit_transform(features)
    pca = PCA(n_components=0.95)
    features_reduced = pca.fit_transform(features_scaled)

    # Metrics
    sil = silhouette_score(features_reduced, clusters)
    db = davies_bouldin_score(features_reduced, clusters)
    
    print(f"Sample Size: {sample_size}")
    print(f"Silhouette Score (PCA Reduced): {sil:.4f}")
    print(f"Davies-Bouldin Index: {db:.4f}")

if __name__ == "__main__":
    evaluate_clustering()
