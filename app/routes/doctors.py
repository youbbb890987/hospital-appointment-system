from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate, DoctorResponse
from app.cache.redis_cache import get_cache, set_cache, clear_cache
from app.core.dependencies import require_admin

router = APIRouter(prefix="/doctors", tags=["Doctors"])


# =========================
# CREATE DOCTOR (ADMIN ONLY)
# =========================
@router.post("/", response_model=DoctorResponse)
def create_doctor(
    doctor: DoctorCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
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

    clear_cache("all_doctors")

    return new_doctor


# =========================
# GET ALL DOCTORS (OPEN)
# =========================
@router.get("/", response_model=list[DoctorResponse])
def get_all_doctors(
    db: Session = Depends(get_db)
):
    cached_doctors = get_cache("all_doctors")

    if cached_doctors:
        return cached_doctors

    doctors = db.query(Doctor).all()

    result = [
        {
            "id": d.id,
            "name": d.name,
            "specialization": d.specialization,
            "phone": d.phone,
            "email": d.email
        }
        for d in doctors
    ]

    set_cache("all_doctors", result)

    return result


# =========================
# GET DOCTOR BY ID (OPEN)
# =========================
@router.get("/{doctor_id}", response_model=DoctorResponse)
def get_doctor_by_id(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    return doctor


# =========================
# UPDATE DOCTOR (ADMIN ONLY)
# =========================
@router.put("/{doctor_id}", response_model=DoctorResponse)
def update_doctor(
    doctor_id: int,
    doctor: DoctorCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
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

    clear_cache("all_doctors")

    return db_doctor


# =========================
# DELETE DOCTOR (ADMIN ONLY)
# =========================
@router.delete("/{doctor_id}")
def delete_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
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

    clear_cache("all_doctors")

    return {
        "message": "Doctor deleted successfully"
    }