from pydantic import BaseModel, Field
from typing import Literal


class AppointmentCreate(BaseModel):
    doctor_id: int = Field(..., gt=0)
    appointment_date: str = Field(..., min_length=5)


class AppointmentStatusUpdate(BaseModel):
    status: Literal["Scheduled", "Completed", "Cancelled"]


class AppointmentResponse(BaseModel):
    id: int
    user_id: int
    doctor_id: int
    appointment_date: str
    status: str

    class Config:
        from_attributes = True