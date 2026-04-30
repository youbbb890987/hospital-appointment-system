from pydantic import BaseModel, EmailStr, Field


class DoctorCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    specialization: str = Field(..., min_length=3, max_length=50)
    phone: str = Field(..., min_length=10, max_length=15)
    email: EmailStr


class DoctorResponse(BaseModel):
    id: int
    name: str
    specialization: str
    phone: str
    email: EmailStr

    class Config:
        from_attributes = True