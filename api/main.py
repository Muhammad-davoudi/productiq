from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
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
from api.routes.analysis import router as analysis_router
from api.routes.kafka_evaluation import router as kafka_router

app.include_router(analytics_router)
app.include_router(assistant_router)
app.include_router(model_management_router)
app.include_router(monitoring_router)
app.include_router(analysis_router)
app.include_router(kafka_router)

@app.get("/api/clustering/profiles")
def get_clustering_profiles_compatibility():
    return {"status": "success", "profiles": [], "message": "Clustering profiles compatibility endpoint"}

@app.get("/")
def root():
    return {"status": "ok", "message": "Digikala AI API is running"}
