from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate, DoctorResponse
from app.cache.redis_cache import get_cache, set_cache

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.post("/", response_model=DoctorResponse)
def create_doctor(
    doctor: DoctorCreate,
    db: Session = Depends(get_db)
):
    existing_doctor = db.query(Doctor).filter(
        Doctor.email == doctor.email
    ).first()

    if existing_doctor:
        raise HTTPException(
            status_code=400,
            detail="Doctor email already exists"
        )

    new_doctor = Doctor(
        name=doctor.name,
        specialization=doctor.specialization,
        phone=doctor.phone,
        email=doctor.email
    )

    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)

    return new_doctor


@router.get("/", response_model=list[DoctorResponse])
def get_all_doctors(
    db: Session = Depends(get_db)
):
    doctors = db.query(Doctor).all()
    return doctors

@router.get("/", response_model=list[DoctorResponse])
def get_all_doctors(
    db: Session = Depends(get_db)
):
    cached_doctors = get_cache("all_doctors")

    if cached_doctors:
        return cached_doctors

    doctors = db.query(Doctor).all()

    set_cache("all_doctors", doctors)

    return doctors

@router.put("/{doctor_id}", response_model=DoctorResponse)
def update_doctor(
    doctor_id: int,
    doctor: DoctorCreate,
    db: Session = Depends(get_db)
):
    db_doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    if not db_doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    db_doctor.name = doctor.name
    db_doctor.specialization = doctor.specialization
    db_doctor.phone = doctor.phone
    db_doctor.email = doctor.email

    db.commit()
    db.refresh(db_doctor)

    return db_doctor


@router.delete("/{doctor_id}")
def delete_doctor(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    db_doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    if not db_doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    db.delete(db_doctor)
    db.commit()

    return {
        "message": "Doctor deleted successfully"
    }