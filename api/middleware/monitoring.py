import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from collections import Counter

# In-memory storage for simple monitoring
request_metrics = {
    "count": 0,
    "errors": 0,
    "total_latency": 0.0
}

class MonitoringMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        try:
            response = await call_next(request)
            request_metrics["count"] += 1
            request_metrics["total_latency"] += (time.time() - start_time)
            return response
        except Exception as e:
            request_metrics["errors"] += 1
            raise e
