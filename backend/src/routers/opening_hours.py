from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import OpeningHours
from schemas import OpeningHours as OpeningHoursSchema, OpeningHoursCreate

router = APIRouter(prefix="/opening-hours", tags=["opening-hours"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[OpeningHoursSchema])
def read_opening_hours(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    opening_hours = db.query(OpeningHours).offset(skip).limit(limit).all()
    return opening_hours


@router.get("/{opening_hours_id}", response_model=OpeningHoursSchema)
def read_opening_hours_item(opening_hours_id: int, db: Session = Depends(get_db)):
    opening_hours = db.query(OpeningHours).filter(OpeningHours.id_opening_hours == opening_hours_id).first()
    if opening_hours is None:
        raise HTTPException(status_code=404, detail="Opening hours not found")
    return opening_hours


@router.post("/", response_model=OpeningHoursSchema)
def create_opening_hours(opening_hours: OpeningHoursCreate, db: Session = Depends(get_db)):
    db_opening_hours = OpeningHours(**opening_hours.model_dump())
    db.add(db_opening_hours)
    db.commit()
    db.refresh(db_opening_hours)
    return db_opening_hours


@router.put("/{opening_hours_id}", response_model=OpeningHoursSchema)
def update_opening_hours(opening_hours_id: int, opening_hours: OpeningHoursCreate, db: Session = Depends(get_db)):
    db_opening_hours = db.query(OpeningHours).filter(OpeningHours.id_opening_hours == opening_hours_id).first()
    if db_opening_hours is None:
        raise HTTPException(status_code=404, detail="Opening hours not found")
    for key, value in opening_hours.model_dump().items():
        setattr(db_opening_hours, key, value)
    db.commit()
    db.refresh(db_opening_hours)
    return db_opening_hours


@router.delete("/{opening_hours_id}")
def delete_opening_hours(opening_hours_id: int, db: Session = Depends(get_db)):
    db_opening_hours = db.query(OpeningHours).filter(OpeningHours.id_opening_hours == opening_hours_id).first()
    if db_opening_hours is None:
        raise HTTPException(status_code=404, detail="Opening hours not found")
    db.delete(db_opening_hours)
    db.commit()
    return {"message": "Opening hours deleted"}

