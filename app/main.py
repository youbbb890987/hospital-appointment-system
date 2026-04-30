from fastapi import FastAPI, Depends
from app.core.database import Base, engine
from app.models.user import User
from app.routes.auth import router as auth_router
from app.core.dependencies import get_current_user
from app.routes.doctors import router as doctors_router
from app.routes.patients import router as patients_router
from app.routes.appointments import router as appointments_router
from app.routes.monitoring import router as monitoring_router

app = FastAPI(
    title="Hospital Appointment System",
    description="Backend project using FastAPI",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(doctors_router)
app.include_router(patients_router)
app.include_router(appointments_router)
app.include_router(monitoring_router)

@app.get("/")
def root():
    return {
        "message": "Hospital Appointment System API is running successfully"
    }


@app.get("/profile")
def get_profile(current_user=Depends(get_current_user)):
    return {
        "message": "Protected Route Accessed",
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "role": current_user.role
        }
    }