import json
import os
import psutil
from typing import Dict, Any

def load_json_safe(filepath: str) -> Dict[str, Any]:
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def get_latest_model_metrics() -> Dict[str, Any]:
    # 1. NLP Metrics
    nlp_eval = load_json_safe("data/processed/nlp_evaluation.json")
    
    # 2. Clustering Evaluation
    clustering_eval = load_json_safe("data/processed/clustering_evaluation.json")
    
    # 3. Recommender Metadata & Weights
    recommender_info = {
        "architecture": "Hybrid (Content-Based + Vector Similarity)",
        "similarity_method": "cosine_similarity",
        "default_top_k": 5,
        "status": "Active",
        "embedding_file": "product_embeddings.npy",
        "scoring_layers": [
            {"name": "شباهت معنایی", "weight": 0.92},
            {"name": "خوشه کالا", "weight": 0.85},
            {"name": "تعامل کاربر", "weight": 0.78},
            {"name": "فیلتر دسته", "weight": 0.70}
        ]
    }

    # 4. MLflow Experiments Summary (if available)
    mlflow_status = "Available"
    latest_run_id = "N/A"
    try:
        from mlflow.tracking import MlflowClient
        client = MlflowClient()
        experiments = client.search_experiments()
        if experiments:
            runs = client.search_runs(
                experiment_ids=[exp.experiment_id for exp in experiments],
                order_by=["start_time DESC"],
                max_results=1
            )
            if runs:
                latest_run_id = runs[0].info.run_id[:8]
    except Exception:
        mlflow_status = "Inactive"

    return {
        "nlp": nlp_eval,
        "clustering": clustering_eval,
        "recommender": recommender_info,
        "mlflow": {
            "status": mlflow_status,
            "latest_run_id": latest_run_id
        }
    }

def get_system_stats() -> Dict[str, Any]:
    vm = psutil.virtual_memory()
    return {
        "system": {
            "cpu_percent": psutil.cpu_percent(interval=None),
            "ram_percent": vm.percent,
            "ram_used_gb": round((vm.total - vm.available) / (1024 ** 3), 2),
            "ram_total_gb": round(vm.total / (1024 ** 3), 2)
        }
    }
