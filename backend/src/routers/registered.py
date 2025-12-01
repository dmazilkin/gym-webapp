from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Registered
from schemas import Registered as RegisteredSchema, RegisteredCreate

router = APIRouter(prefix="/registered", tags=["registered"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[RegisteredSchema])
def read_registered(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    registered = db.query(Registered).offset(skip).limit(limit).all()
    return registered


@router.get("/{registered_id}", response_model=RegisteredSchema)
def read_registered_item(registered_id: int, db: Session = Depends(get_db)):
    registered = db.query(Registered).filter(Registered.id_registered == registered_id).first()
    if registered is None:
        raise HTTPException(status_code=404, detail="Registered not found")
    return registered


@router.post("/", response_model=RegisteredSchema)
def create_registered(registered: RegisteredCreate, db: Session = Depends(get_db)):
    db_registered = Registered(**registered.model_dump())
    db.add(db_registered)
    db.commit()
    db.refresh(db_registered)
    return db_registered


@router.put("/{registered_id}", response_model=RegisteredSchema)
def update_registered(registered_id: int, registered: RegisteredCreate, db: Session = Depends(get_db)):
    db_registered = db.query(Registered).filter(Registered.id_registered == registered_id).first()
    if db_registered is None:
        raise HTTPException(status_code=404, detail="Registered not found")
    for key, value in registered.model_dump().items():
        setattr(db_registered, key, value)
    db.commit()
    db.refresh(db_registered)
    return db_registered


@router.delete("/{registered_id}")
def delete_registered(registered_id: int, db: Session = Depends(get_db)):
    db_registered = db.query(Registered).filter(Registered.id_registered == registered_id).first()
    if db_registered is None:
        raise HTTPException(status_code=404, detail="Registered not found")
    db.delete(db_registered)
    db.commit()
    return {"message": "Registered deleted"}

