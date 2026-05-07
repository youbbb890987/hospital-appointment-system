import time
from fastapi import FastAPI, Depends, Request
from fastapi.responses import Response
from app.core.database import Base, engine
from app.models.user import User
from app.routes.auth import router as auth_router
from app.core.dependencies import get_current_user
from app.routes.doctors import router as doctors_router
from app.routes.patients import router as patients_router
from app.routes.appointments import router as appointments_router
from app.routes.monitoring import router as monitoring_router
from fastapi.middleware.cors import CORSMiddleware
from app.core.logger import logger


app = FastAPI(
    title="Hospital Appointment System",
    description="Backend project using FastAPI",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)


# =========================
# LOGGING MIDDLEWARE
# =========================
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Log incoming request
    logger.info(f"REQUEST | {request.method} {request.url.path} | Client: {request.client.host}")

    try:
        response = await call_next(request)
        process_time = round((time.time() - start_time) * 1000, 2)

        # Log level based on status code
        if response.status_code >= 500:
            logger.error(f"RESPONSE | {request.method} {request.url.path} | Status: {response.status_code} | Time: {process_time}ms")
        elif response.status_code >= 400:
            logger.warning(f"RESPONSE | {request.method} {request.url.path} | Status: {response.status_code} | Time: {process_time}ms")
        else:
            logger.info(f"RESPONSE | {request.method} {request.url.path} | Status: {response.status_code} | Time: {process_time}ms")

        response.headers["X-Process-Time"] = str(process_time)
        return response

    except Exception as e:
        process_time = round((time.time() - start_time) * 1000, 2)
        logger.critical(f"ERROR | {request.method} {request.url.path} | Exception: {str(e)} | Time: {process_time}ms")
        raise


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(doctors_router)
app.include_router(patients_router)
app.include_router(appointments_router)
app.include_router(monitoring_router)


@app.get("/")
def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Hospital Appointment System API is running successfully"
    }


@app.get("/profile")
def get_profile(current_user=Depends(get_current_user)):
    logger.info(f"Profile accessed by user: {current_user.email} | Role: {current_user.role}")
    return {
        "message": "Protected Route Accessed",
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "role": current_user.role
        }
    }