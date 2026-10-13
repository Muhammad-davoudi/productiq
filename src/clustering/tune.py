import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import os
import sys
import mlflow
from src.utils.mlflow_logger import MLFlowTracker

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def run_tuning():
    matrix_path = 'data/processed/product_feature_matrix.csv'
    df = pd.read_csv(matrix_path)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    features = df[numeric_cols].values
    
    # Scale
    features_scaled = StandardScaler().fit_transform(features)
    
    # Sample for Silhouette (due to RAM constraints)
    sample_size = min(10000, len(features_scaled))
    features_sample = features_scaled[np.random.choice(features_scaled.shape[0], sample_size, replace=False)]

    k_values = range(2, 10)
    wcss = []
    silhouette_scores = []

    print(f"Tuning KMeans on sample size: {sample_size}...")
    for k in k_values:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=5)
        labels = kmeans.fit_predict(features_scaled)
        wcss.append(kmeans.inertia_)
        
        # Calculate silhouette on sample
        labels_sample = kmeans.predict(features_sample)
        score = silhouette_score(features_sample, labels_sample)
        silhouette_scores.append(score)
        print(f"K={k} | WCSS={kmeans.inertia_:.2f} | Silhouette={score:.4f}")

    # Plotting
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(k_values, wcss, 'bo-', label='WCSS (Inertia)')
    ax1.set_xlabel('Number of Clusters (K)')
    ax1.set_ylabel('WCSS', color='b')
    
    ax2 = ax1.twinx()
    ax2.plot(k_values, silhouette_scores, 'ro-', label='Silhouette Score')
    ax2.set_ylabel('Silhouette Score', color='r')
    
    plt.title('KMeans Elbow Method & Silhouette Analysis')
    plot_path = "clustering_tuning.png"
    plt.savefig(plot_path)
    
    # Log to MLflow
    tracker = MLFlowTracker(experiment_name="Digikala_Clustering_Tuning")
    tracker.log_run(params={"k_range": "2-10"}, metrics={"best_silhouette": max(silhouette_scores)})
    mlflow.log_artifact(plot_path)
    print(f"Tuning complete. Plot saved as artifact.")

if __name__ == "__main__":
    run_tuning()
