import mlflow
from fastapi import APIRouter, HTTPException
from mlflow.tracking import MlflowClient
from api.middleware.monitoring import request_metrics
from typing import List, Dict, Any

router = APIRouter(prefix="/api/models", tags=["model-management"])
client = MlflowClient()

@router.get("/experiments")
def get_experiments():
    try:
        experiments = client.search_experiments()
        return [
            {
                "id": exp.experiment_id,
                "name": exp.name,
                "lifecycle_stage": exp.lifecycle_stage,
                "creation_time": exp.creation_time
            } for exp in experiments
        ]
    except Exception as e:
        return {"error": str(e)}

@router.get("/runs/{experiment_id}")
def get_runs(experiment_id: str):
    try:
        runs = client.search_runs(experiment_ids=[experiment_id])
        return [
            {
                "run_id": run.info.run_id,
                "status": run.info.status,
                "start_time": run.info.start_time,
                "metrics": run.data.metrics,
                "params": run.data.params
            } for run in runs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/versions")
def get_model_versions():
    try:
        models = client.search_registered_models()
        results = []
        for model in models:
            for version in model.latest_versions:
                results.append({
                    "name": model.name,
                    "version": version.version,
                    "stage": version.current_stage,
                    "run_id": version.run_id,
                    "creation_timestamp": version.creation_timestamp
                })
        return {"models": results}
    except Exception as e:
        return {"error": str(e)}

@router.get("/monitoring")
def get_monitoring():
    count = request_metrics["count"]
    latency = request_metrics["total_latency"] / count if count > 0 else 0
    return {
        "request_count": count,
        "avg_latency": round(latency, 4),
        "error_count": request_metrics["errors"],
        "status": "operational"
    }
