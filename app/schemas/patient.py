from pydantic import BaseModel, Field


class PatientCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    age: int = Field(..., ge=0, le=120)
    gender: str = Field(..., min_length=3, max_length=10)
    phone: str = Field(..., min_length=10, max_length=15)


class PatientResponse(BaseModel):
    id: int
    name: str
    age: int
    gender: str
    phone: str

    class Config:
        from_attributes = True