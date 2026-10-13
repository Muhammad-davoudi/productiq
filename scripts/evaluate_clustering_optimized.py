import pandas as pd
import numpy as np
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.preprocessing import StandardScaler
import os

# Paths
matrix_path = 'data/processed/product_feature_matrix.csv'
clusters_path = 'data/processed/product_clusters.csv'

def run_optimized_eval():
    print("\n--- Optimized Clustering Evaluation (With StandardScaler) ---")
    
    df_features = pd.read_csv(matrix_path)
    df_clusters = pd.read_csv(clusters_path)
    
    # 1. Take sample for performance
    if len(df_features) > 200:
        df_eval = df_features.sample(n=200, random_state=42)
        indices = df_eval.index
        features = df_eval.select_dtypes(include=[np.number]).values
        clusters = df_clusters.loc[indices, 'cluster_id'].values
    else:
        features = df_features.select_dtypes(include=[np.number]).values
        clusters = df_clusters['cluster_id'].values
    
    # 2. APPLY SCALING (The fix)
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    # 3. Evaluate
    sil = silhouette_score(features_scaled, clusters)
    db = davies_bouldin_score(features_scaled, clusters)
    
    print(f"Silhouette Score (Optimized): {sil:.4f}")
    print(f"Davies-Bouldin Index (Optimized): {db:.4f}")
    
    if sil > 0:
        print("Success: Scaling improved the structure.")
    else:
        print("Note: Scaling didn't solve the issue; the features themselves might be noise.")

if __name__ == "__main__":
    run_optimized_eval()
