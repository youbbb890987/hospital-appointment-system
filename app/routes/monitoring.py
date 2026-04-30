from fastapi import APIRouter
import os

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])

REQUEST_COUNT = 0


@router.get("/stats")
def get_stats():
    global REQUEST_COUNT
    REQUEST_COUNT += 1

    return {
        "total_requests": REQUEST_COUNT,
        "status": "Running",
        "message": "Monitoring dashboard working"
    }


@router.get("/logs")
def get_logs():
    if not os.path.exists("app.log"):
        return {"message": "No logs yet"}

    with open("app.log", "r") as f:
        logs = f.readlines()[-10:]

    return {
        "recent_logs": logs
    }