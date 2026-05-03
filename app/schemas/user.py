from pydantic import BaseModel, EmailStr, Field
from typing import Optional


# =========================
# REGISTER
# =========================
class UserRegister(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=50)

    # 🔥 اضف دي
    role: str = Field(default="user")


# =========================
# UPDATE PROFILE
# =========================
class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6, max_length=50)


# =========================
# RESPONSE
# =========================
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True