from pydantic import BaseModel, Field


# =========================
# CREATE
# =========================
class AppointmentCreate(BaseModel):
    doctor_id: int = Field(..., gt=0)
    appointment_date: str = Field(..., min_length=5)


# =========================
# RESPONSE
# =========================
class AppointmentResponse(BaseModel):
    id: int
    user_id: int  
    doctor_id: int
    appointment_date: str
    status: str

    class Config:
        from_attributes = True