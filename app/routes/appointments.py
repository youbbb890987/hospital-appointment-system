from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.schemas.appointment import AppointmentCreate, AppointmentResponse
from app.core.dependencies import get_current_user, require_admin
from app.models.user import User

router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)


# =========================
# CREATE APPOINTMENT (USER)
# =========================
@router.post("/", response_model=AppointmentResponse)
def create_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # check doctor exists
    doctor = db.query(Doctor).filter(
        Doctor.id == appointment.doctor_id
    ).first()

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # ❗ منع تضارب لنفس الدكتور في نفس الوقت
    conflict = db.query(Appointment).filter(
        Appointment.doctor_id == appointment.doctor_id,
        Appointment.appointment_date == appointment.appointment_date
    ).first()

    if conflict:
        raise HTTPException(
            status_code=400,
            detail="This time slot is already booked"
        )

    new_appointment = Appointment(
        user_id=current_user.id,
        doctor_id=appointment.doctor_id,
        appointment_date=appointment.appointment_date,
        status="Pending"
    )

    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    return new_appointment


# =========================
# GET MY APPOINTMENTS (USER)
# =========================
@router.get("/my", response_model=list[AppointmentResponse])
def get_my_appointments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Appointment).filter(
        Appointment.user_id == current_user.id
    ).all()


# =========================
# UPDATE MY APPOINTMENT (USER)
# =========================
@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()

    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # ❗ user يعدل بس بتاعه
    if db_appointment.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not allowed"
        )

    # ❗ check conflict
    conflict = db.query(Appointment).filter(
        Appointment.doctor_id == appointment.doctor_id,
        Appointment.appointment_date == appointment.appointment_date,
        Appointment.id != appointment_id
    ).first()

    if conflict:
        raise HTTPException(
            status_code=400,
            detail="Time slot already booked"
        )

    db_appointment.doctor_id = appointment.doctor_id
    db_appointment.appointment_date = appointment.appointment_date

    db.commit()
    db.refresh(db_appointment)

    return db_appointment


# =========================
# DELETE MY APPOINTMENT (USER)
# =========================
@router.delete("/{appointment_id}")
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if appointment.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not allowed"
        )

    db.delete(appointment)
    db.commit()

    return {"message": "Appointment deleted"}


# =========================
# ADMIN: GET ALL APPOINTMENTS
# =========================
@router.get("/", response_model=list[AppointmentResponse])
def get_all_appointments(
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    return db.query(Appointment).all()


# =========================
# ADMIN: DELETE ANY APPOINTMENT
# =========================
@router.delete("/admin/{appointment_id}")
def admin_delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    db.delete(appointment)
    db.commit()

    return {"message": "Deleted by admin"}