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
