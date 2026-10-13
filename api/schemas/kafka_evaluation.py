from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class KafkaEvaluationRun(BaseModel):
    id: str
    status: str  # "pending", "running", "completed", "failed"
    start_time: datetime
    end_time: Optional[datetime] = None
    result_summary: Optional[Dict[str, Any]] = None
