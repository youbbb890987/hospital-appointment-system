from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.schemas.appointment import AppointmentCreate, AppointmentResponse

router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)


@router.post("/", response_model=AppointmentResponse)
def create_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(
        Patient.id == appointment.patient_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    doctor = db.query(Doctor).filter(
        Doctor.id == appointment.doctor_id
    ).first()

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    new_appointment = Appointment(
        patient_id=appointment.patient_id,
        doctor_id=appointment.doctor_id,
        appointment_date=appointment.appointment_date,
        status="Pending"
    )

    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    return new_appointment


@router.get("/", response_model=list[AppointmentResponse])
def get_all_appointments(
    db: Session = Depends(get_db)
):
    return db.query(Appointment).all()


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment_by_id(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    return appointment
@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    appointment: AppointmentCreate,
    db: Session = Depends(get_db)
):
    db_appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()

    if not db_appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    db_appointment.patient_id = appointment.patient_id
    db_appointment.doctor_id = appointment.doctor_id
    db_appointment.appointment_date = appointment.appointment_date

    db.commit()
    db.refresh(db_appointment)

    return db_appointment


@router.delete("/{appointment_id}")
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    db_appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()

    if not db_appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    db.delete(db_appointment)
    db.commit()

    return {
        "message": "Appointment deleted successfully"
    }