import mlflow
from mlflow.tracking import MlflowClient
import psutil

def get_latest_model_metrics():
    client = MlflowClient()
    experiments = client.search_experiments()
    if not experiments:
        return {"status": "N/A", "accuracy": "N/A", "f1_score": "N/A", "version": "N/A"}

    runs = client.search_runs(experiment_ids=[experiments[0].experiment_id], order_by=["start_time DESC"], max_results=1)
    
    if not runs:
        return {"status": "N/A", "accuracy": "N/A", "f1_score": "N/A", "version": "N/A"}

    run = runs[0]
    metrics = run.data.metrics
    
    return {
        "status": metrics.get("status", "N/A"),
        "accuracy": metrics.get("accuracy", "N/A"),
        "f1_score": metrics.get("f1_score", "N/A"),
        "version": run.info.run_id[:8]
    }

def get_system_stats():
    return {
        "cpu": psutil.cpu_percent(interval=1),
        "ram": psutil.virtual_memory().percent
    }
