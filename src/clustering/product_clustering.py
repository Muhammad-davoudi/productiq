import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import os
import sys
from src.utils.mlflow_logger import MLFlowTracker

# Add project root to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

MATRIX_PATH = 'data/processed/product_feature_matrix.csv'
CLUSTER_OUTPUT_PATH = 'data/processed/product_clusters.csv'

def run_pipeline():
    print(f"Loading features from {MATRIX_PATH}...")
    df = pd.read_csv(MATRIX_PATH)

    # Select numeric features
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    features = df[numeric_cols].values

    # 1. Scale
    print("Scaling features...")
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    # 2. PCA (Keeping 95% variance)
    print("Applying PCA...")
    pca = PCA(n_components=0.95)
    features_pca = pca.fit_transform(features_scaled)
    print(f"Reduced to {features_pca.shape[1]} dimensions.")

    # 3. K-Means (K=7 based on Phase 8 evaluation)
    n_clusters = 7
    print(f"Running KMeans (K={n_clusters})...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(features_pca)

    # Assign labels
    df['cluster'] = labels

    # Save
    print(f"Saving results to {CLUSTER_OUTPUT_PATH}...")
    df.to_csv(CLUSTER_OUTPUT_PATH, index=False)

    # Summary
    print("\nCluster Distribution:")
    print(df['cluster'].value_counts().sort_index())
    print("-" * 30)

    # MLflow Logging
    params = {"n_clusters": n_clusters, "pca_components": pca.n_components_}
    metrics = {"inertia": kmeans.inertia_}
    
    tracker = MLFlowTracker(experiment_name="Digikala_Clustering")
    tracker.log_run(params=params, metrics=metrics)
    print("Clustering metrics logged to MLflow.", flush=True)
    print("Clustering pipeline complete.")

if __name__ == "__main__":
    run_pipeline()
