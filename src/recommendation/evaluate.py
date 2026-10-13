import json
import os
import sys
import pandas as pd
from src.utils.mlflow_logger import MLFlowTracker

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def evaluate_recommendations():
    recs_path = "data/recommendations.json"
    matrix_path = "data/processed/product_feature_matrix.csv"
    
    if not os.path.exists(recs_path) or not os.path.exists(matrix_path):
        print("Error: Required files not found for evaluation.")
        return

    # Load recommendations
    with open(recs_path, 'r', encoding='utf-8') as f:
        recs = json.load(f)

    # Load full catalog to get accurate denominator
    df_catalog = pd.read_csv(matrix_path)
    total_catalog_size = len(df_catalog)

    # Calculate metrics
    all_recommended = [item for sublist in recs.values() for item in sublist]
    unique_rec_items = set(all_recommended)
    
    avg_recs = len(all_recommended) / len(recs) if len(recs) > 0 else 0
    coverage = len(unique_rec_items) / total_catalog_size if total_catalog_size > 0 else 0

    metrics = {
        "avg_recs_per_product": float(avg_recs),
        "catalog_coverage": float(coverage)
    }
    
    tracker = MLFlowTracker(experiment_name="Digikala_Recommender_Performance")
    tracker.log_run(params={"total_sources": len(recs), "catalog_size": total_catalog_size}, metrics=metrics)
    print(f"Metrics logged: {metrics}")

if __name__ == "__main__":
    evaluate_recommendations()
