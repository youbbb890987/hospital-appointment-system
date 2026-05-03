from sqlalchemy import Column, Integer, String, ForeignKey
from app.core.database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)

    # 👤 user owner
    user_id = Column(Integer, ForeignKey("users.id"))

    # 👨‍⚕️ doctor
    doctor_id = Column(Integer, ForeignKey("doctors.id"))

    appointment_date = Column(String, nullable=False)

    status = Column(String, default="Pending")



