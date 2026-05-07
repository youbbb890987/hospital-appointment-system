from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.schemas.appointment import AppointmentCreate, AppointmentResponse, AppointmentStatusUpdate
from app.core.dependencies import get_current_user, require_admin
from app.cache.redis_cache import get_cache, set_cache, clear_cache
from app.models.user import User

router = APIRouter(prefix="/appointments", tags=["Appointments"])

VALID_STATUSES = ["Scheduled", "Completed", "Cancelled"]


def parse_date(date_str):
    for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(str(date_str).strip(), fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {date_str}")


def check_time_conflict(db, doctor_id, appointment_date, exclude_id=None):
    try:
        date = parse_date(appointment_date)
    except ValueError:
        return None
    one_hour_before = date - timedelta(hours=1)
    one_hour_after = date + timedelta(hours=1)
    query = db.query(Appointment).filter(Appointment.doctor_id == doctor_id)
    if exclude_id:
        query = query.filter(Appointment.id != exclude_id)
    for appt in query.all():
        try:
            appt_date = parse_date(appt.appointment_date)
            if one_hour_before < appt_date < one_hour_after:
                return appt
        except ValueError:
            continue
    return None


@router.post("/", response_model=AppointmentResponse)
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    doctor = db.query(Doctor).filter(Doctor.id == appointment.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    conflict = check_time_conflict(db, appointment.doctor_id, appointment.appointment_date)
    if conflict:
        raise HTTPException(status_code=400, detail="This time slot is already booked. Please choose a different time (at least 1 hour apart).")
    new_appointment = Appointment(user_id=current_user.id, doctor_id=appointment.doctor_id, appointment_date=appointment.appointment_date, status="Scheduled")
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    clear_cache("all_appointments")
    clear_cache(f"my_appointments_{current_user.id}")
    return new_appointment


@router.get("/my", response_model=list[AppointmentResponse])
def get_my_appointments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cache_key = f"my_appointments_{current_user.id}"
    cached = get_cache(cache_key)
    if cached:
        return cached
    appointments = db.query(Appointment).filter(Appointment.user_id == current_user.id).all()
    result = [{"id": a.id, "user_id": a.user_id, "doctor_id": a.doctor_id, "appointment_date": a.appointment_date, "status": a.status} for a in appointments]
    set_cache(cache_key, result)
    return appointments


@router.get("/", response_model=list[AppointmentResponse])
def get_all_appointments(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    cached = get_cache("all_appointments")
    if cached:
        return cached
    appointments = db.query(Appointment).all()
    result = [{"id": a.id, "user_id": a.user_id, "doctor_id": a.doctor_id, "appointment_date": a.appointment_date, "status": a.status} for a in appointments]
    set_cache("all_appointments", result)
    return appointments


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment_by_id(appointment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if current_user.role != "admin" and appointment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    return appointment


@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(appointment_id: int, appointment: AppointmentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if current_user.role != "admin" and db_appointment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    doctor = db.query(Doctor).filter(Doctor.id == appointment.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    conflict = check_time_conflict(db, appointment.doctor_id, appointment.appointment_date, exclude_id=appointment_id)
    if conflict:
        raise HTTPException(status_code=400, detail="This time slot is already booked. Please choose a different time (at least 1 hour apart).")
    db_appointment.doctor_id = appointment.doctor_id
    db_appointment.appointment_date = appointment.appointment_date
    db.commit()
    db.refresh(db_appointment)
    clear_cache("all_appointments")
    clear_cache(f"appointment_{appointment_id}")
    clear_cache(f"my_appointments_{current_user.id}")
    return db_appointment


@router.patch("/{appointment_id}/status", response_model=AppointmentResponse)
def update_appointment_status(appointment_id: int, status_update: AppointmentStatusUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if status_update.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}")
    appointment.status = status_update.status
    db.commit()
    db.refresh(appointment)
    clear_cache("all_appointments")
    clear_cache(f"appointment_{appointment_id}")
    clear_cache(f"my_appointments_{appointment.user_id}")
    return appointment


@router.delete("/{appointment_id}")
def delete_appointment(appointment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if current_user.role != "admin" and appointment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    user_id = appointment.user_id
    db.delete(appointment)
    db.commit()
    clear_cache("all_appointments")
    clear_cache(f"appointment_{appointment_id}")
    clear_cache(f"my_appointments_{user_id}")
    return {"message": "Appointment deleted"}