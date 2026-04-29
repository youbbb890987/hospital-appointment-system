from pydantic import BaseModel, EmailStr


class DoctorCreate(BaseModel):
    name: str
    specialization: str
    phone: str
    email: EmailStr


class DoctorResponse(BaseModel):
    id: int
    name: str
    specialization: str
    phone: str
    email: EmailStr

    class Config:
        from_attributes = True