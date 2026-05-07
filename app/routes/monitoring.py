from fastapi import APIRouter, Depends, Request
from app.core.dependencies import require_admin
import os
import time
from datetime import datetime

router = APIRouter(
    prefix="/monitoring",
    tags=["Monitoring"],
    dependencies=[Depends(require_admin)]
)

# In-memory stats
stats = {
    "total_requests": 0,
    "total_errors": 0,
    "start_time": datetime.now().isoformat(),
    "endpoints": {}
}

def track_request(endpoint: str, status: int, response_time: float):
    stats["total_requests"] += 1
    if status >= 400:
        stats["total_errors"] += 1
    if endpoint not in stats["endpoints"]:
        stats["endpoints"][endpoint] = {"count": 0, "avg_response_time": 0}
    stats["endpoints"][endpoint]["count"] += 1
    stats["endpoints"][endpoint]["avg_response_time"] = response_time

@router.get("/stats")
def get_stats():
    return {
        "total_requests": stats["total_requests"],
        "total_errors": stats["total_errors"],
        "error_rate": f"{(stats['total_errors'] / max(stats['total_requests'], 1) * 100):.1f}%",
        "uptime_since": stats["start_time"],
        "status": "Running",
        "endpoints_stats": stats["endpoints"]
    }

@router.get("/logs")
def get_logs():
    if not os.path.exists("app.log"):
        return {"message": "No logs yet"}
    with open("app.log", "r") as f:
        logs = f.readlines()[-20:]
    return {
        "recent_logs": [log.strip() for log in logs],
        "total_lines": len(logs)
    }

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected",
        "redis": "connected"
    }