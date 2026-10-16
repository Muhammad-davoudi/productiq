import os
import time
from fastapi import APIRouter
from sqlalchemy import text
from .service import get_latest_model_metrics, get_system_stats

router = APIRouter(prefix="/api/monitoring")

@router.get("/stats")
async def get_stats():
    model_data = get_latest_model_metrics()
    system_data = get_system_stats()
    return {
        **model_data,
        **system_data
    }

# راتر جداگانه برای درخواست‌های کافکا که فرانت‌اند مستقیماً به /api/kafka_evaluation می‌فرستد
kafka_router = APIRouter(prefix="/api/kafka_evaluation")

@kafka_router.get("/active")
def get_active_kafka_evaluation():
    try:
        with engine.connect() as conn:
            row = conn.execute(text("SELECT id, status FROM kafka_evaluation_runs ORDER BY id DESC LIMIT 1;")).fetchone()
            if row and row[1] == "running":
                return {"eval_id": row[0], "status": "running"}
        return {"eval_id": None, "status": "idle"}
    except Exception:
        return {"eval_id": None, "status": "idle"}

@kafka_router.post("/start")
def start_kafka_simulation():
    try:
        with engine.begin() as conn:
            result = conn.execute(text("INSERT INTO kafka_evaluation_runs (status, created_at) VALUES ('running', NOW()) RETURNING id;"))
            eval_id = result.fetchone()[0]
        return {"status": "success", "eval_id": eval_id}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@kafka_router.get("/status/{eval_id}")
def get_kafka_simulation_status(eval_id: int):
    try:
        with engine.connect() as conn:
            run_row = conn.execute(text("SELECT status FROM kafka_evaluation_runs WHERE id = :eid;"), {"eid": eval_id}).fetchone()
            status = run_row[0] if run_row else "idle"
            
            sent_rows = conn.execute(text("SELECT sentiment, COUNT(*) as count FROM kafka_sentiment_results GROUP BY sentiment;")).fetchall()
            sentiment_distribution = [{"sentiment": r[0], "count": r[1]} for r in sent_rows]
            
            clust_rows = conn.execute(text("SELECT cluster, COUNT(*) as count FROM kafka_clustering_results GROUP BY cluster;")).fetchall()
            clustering_distribution = [{"cluster": r[0], "count": r[1]} for r in clust_rows]
            
            sent_msg_count = conn.execute(text("SELECT COUNT(*) FROM kafka_sentiment_results;")).scalar() or 0
            clust_msg_count = conn.execute(text("SELECT COUNT(*) FROM kafka_clustering_results;")).scalar() or 0
            
        return {
            "status": status,
            "sentiment_distribution": sentiment_distribution,
            "clustering_distribution": clustering_distribution,
            "sentiment_stats": {"messages": sent_msg_count},
            "clustering_stats": {"messages": clust_msg_count}
        }
    except Exception as e:
        return {
            "status": "running",
            "sentiment_distribution": [],
            "clustering_distribution": [],
            "sentiment_stats": {"messages": 0},
            "clustering_stats": {"messages": 0},
            "error": str(e)
        }

@kafka_router.post("/stop/{eval_id}")
def stop_kafka_simulation(eval_id: int):
    try:
        with engine.begin() as conn:
            conn.execute(text("UPDATE kafka_evaluation_runs SET status = 'stopped' WHERE id = :eid;"), {"eid": eval_id})
        return {"status": "success", "message": f"Simulation #{eval_id} stopped."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@kafka_router.post("/reset")
def reset_kafka_simulation_data():
    try:
        with engine.begin() as conn:
            conn.execute(text("TRUNCATE TABLE kafka_sentiment_results, kafka_clustering_results, kafka_evaluation_runs RESTART IDENTITY CASCADE;"))
        return {"status": "success", "message": "Simulation and Kafka results successfully reset."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
