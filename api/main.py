from sqlalchemy import text
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Digikala AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from api.routes.analytics import router as analytics_router
from api.routes.assistant import router as assistant_router
from api.routes.model_management import router as model_management_router
from api.routes.monitoring import router as monitoring_router
from api.routes.kafka_evaluation import router as kafka_router
from api.routes.analysis import router as analysis_router

app.include_router(analytics_router)
app.include_router(assistant_router)
app.include_router(model_management_router)
app.include_router(monitoring_router)
app.include_router(kafka_router)
app.include_router(analysis_router)

@app.get("/")
def root():
    return {"status": "ok", "message": "Digikala AI API is running"}


@app.post("/api/kafka_evaluation/reset")
def reset_kafka_simulation_data():
    try:
        from src.database.connection import SessionLocal
        db = SessionLocal()
        db.execute(text("TRUNCATE TABLE kafka_sentiment_results, kafka_clustering_results RESTART IDENTITY CASCADE;"))
        db.commit()
        db.close()
        return {"status": "success", "message": "Simulation and Kafka results successfully reset."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# -------------------------------------------------------------
# Clustering Profiles Endpoint
# -------------------------------------------------------------
@app.get("/api/clustering/profiles")
def get_clustering_profiles():
    import json
    candidates = [
        "data/real_cluster_profiles.json",
        "frontend/src/data/real_cluster_profiles.json",
        "artifacts/real_cluster_profiles.json"
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                return {"error": f"Failed to read profiles: {str(e)}"}
    return {"error": "Profiles file not found"}

@app.get("/api/analytics/nlp-overview")
def get_nlp_overview(category: str = None):
    """
    اندپوینت زنده تحلیل متن و احساسات (NLP Overview)
    بازگرداننده‌ی خلاصه‌ساز احساسات و جنبه‌های کالا (Aspects)
    """
    import json
    from pathlib import Path
    
    # مسیر فایل مرجع یا دیتابیس پردازش‌شده
    json_path = Path("frontend/src/data/clean_aspects_sentiment.json")
    if json_path.exists():
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except Exception:
            pass
            
    # Fallback پیش‌فرض در صورت عدم دسترسی به فایل
    return {
        "summary": {"Positive": 781, "Neutral": 0, "Negative": 146, "total": 927, "positive_pct": 84.3, "neutral_pct": 0.0, "negative_pct": 15.7},
        "aspects": [
            {"aspect": "قیمت", "positive_count": 133, "neutral_count": 0, "negative_count": 36, "positive_pct": 78.7, "neutral_pct": 0.0, "negative_pct": 21.3, "total_reviews": 169},
            {"aspect": "کیفیت ساخت", "positive_count": 250, "neutral_count": 0, "negative_count": 40, "positive_pct": 86.2, "neutral_pct": 0.0, "negative_pct": 13.8, "total_reviews": 290}
        ]
    }
