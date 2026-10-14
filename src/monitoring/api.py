from fastapi import APIRouter
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

@router.post("/kafka_evaluation/reset")
def reset_kafka_simulation_data():
    try:
        from src.database.connection import get_db_connection
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("TRUNCATE TABLE kafka_sentiment_results, kafka_clustering_results RESTART IDENTITY CASCADE;")
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success", "message": "Simulation and Kafka results successfully reset."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
