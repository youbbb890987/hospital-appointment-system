from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientResponse
from app.core.dependencies import get_current_user, require_admin
from app.cache.redis_cache import get_cache, set_cache, clear_cache
from app.models.user import User

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post("/", response_model=PatientResponse)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_patient = Patient(
        name=patient.name, age=patient.age, gender=patient.gender,
        phone=patient.phone, email=patient.email, created_by=current_user.id
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    clear_cache("all_patients")
    clear_cache(f"my_patients_{current_user.id}")
    return new_patient


@router.get("/", response_model=list[PatientResponse])
def get_all_patients(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    cached = get_cache("all_patients")
    if cached:
        return cached
    patients = db.query(Patient).all()
    result = [{"id": p.id, "name": p.name, "age": p.age, "gender": p.gender, "phone": p.phone, "email": p.email, "created_by": p.created_by} for p in patients]
    set_cache("all_patients", result)
    return patients


@router.get("/my", response_model=list[PatientResponse])
def get_my_patients(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cache_key = f"my_patients_{current_user.id}"
    cached = get_cache(cache_key)
    if cached:
        return cached
    patients = db.query(Patient).filter(Patient.created_by == current_user.id).all()
    result = [{"id": p.id, "name": p.name, "age": p.age, "gender": p.gender, "phone": p.phone, "email": p.email, "created_by": p.created_by} for p in patients]
    set_cache(cache_key, result)
    return patients


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient_by_id(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if current_user.role != "admin" and patient.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    return patient


@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(patient_id: int, patient: PatientCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if current_user.role != "admin" and db_patient.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    db_patient.name = patient.name
    db_patient.age = patient.age
    db_patient.gender = patient.gender
    db_patient.phone = patient.phone
    db_patient.email = patient.email
    db.commit()
    db.refresh(db_patient)
    clear_cache("all_patients")
    clear_cache(f"patient_{patient_id}")
    clear_cache(f"my_patients_{current_user.id}")
    return db_patient


@router.delete("/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if current_user.role != "admin" and db_patient.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    owner_id = db_patient.created_by
    db.delete(db_patient)
    db.commit()
    clear_cache("all_patients")
    clear_cache(f"patient_{patient_id}")
    clear_cache(f"my_patients_{owner_id}")
    return {"message": "Patient deleted successfully"}