from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientResponse

router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


@router.post("/", response_model=PatientResponse)
def create_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db)
):
    new_patient = Patient(
        name=patient.name,
        age=patient.age,
        gender=patient.gender,
        phone=patient.phone
    )

    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    return new_patient


@router.get("/", response_model=list[PatientResponse])
def get_all_patients(
    db: Session = Depends(get_db)
):
    return db.query(Patient).all()


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient_by_id(
    patient_id: int,
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return patient
@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: int,
    patient: PatientCreate,
    db: Session = Depends(get_db)
):
    db_patient = db.query(Patient).filter(
        Patient.id == patient_id
    ).first()

    if not db_patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    db_patient.name = patient.name
    db_patient.age = patient.age
    db_patient.gender = patient.gender
    db_patient.phone = patient.phone

    db.commit()
    db.refresh(db_patient)

    return db_patient


@router.delete("/{patient_id}")
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db)
):
    db_patient = db.query(Patient).filter(
        Patient.id == patient_id
    ).first()

    if not db_patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    db.delete(db_patient)
    db.commit()

    return {
        "message": "Patient deleted successfully"
    }