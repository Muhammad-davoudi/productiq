import pandas as pd
import numpy as np
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import os

# Paths
matrix_path = 'data/processed/product_feature_matrix.csv'

def find_best_params():
    print("\n--- Searching for Optimal Clustering Configuration (Using Sample) ---")
    df_features = pd.read_csv(matrix_path)
    
    # Sampling: 50,000 rows is enough to find the mathematical pattern for K
    sample_size = min(50000, len(df_features))
    df_sample = df_features.sample(n=sample_size, random_state=42)
    
    features = df_sample.select_dtypes(include=[np.number]).values
    
    # 1. Scale
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    # 2. PCA
    pca = PCA(n_components=0.95)
    features_pca = pca.fit_transform(features_scaled)
    print(f"PCA reduced {features.shape[1]} features to {features_pca.shape[1]} dimensions.")
    
    # 3. Test K range
    best_k = 0
    best_score = -1
    
    print(f"Testing K values (on {sample_size} samples)...")
    for k in range(2, 11):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(features_pca)
        score = silhouette_score(features_pca, labels)
        print(f"K={k} -> Silhouette Score: {score:.4f}")
        
        if score > best_score:
            best_score = score
            best_k = k
            
    print(f"\nOptimal K found: {best_k} with Score: {best_score:.4f}")

if __name__ == "__main__":
    find_best_params()
