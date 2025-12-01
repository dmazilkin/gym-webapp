from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Trainer
from schemas import Trainer as TrainerSchema, TrainerCreate

router = APIRouter(prefix="/trainers", tags=["trainers"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[TrainerSchema])
def read_trainers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    trainers = db.query(Trainer).offset(skip).limit(limit).all()
    return trainers


@router.get("/{trainer_id}", response_model=TrainerSchema)
def read_trainer(trainer_id: int, db: Session = Depends(get_db)):
    trainer = db.query(Trainer).filter(Trainer.id_trainer == trainer_id).first()
    if trainer is None:
        raise HTTPException(status_code=404, detail="Trainer not found")
    return trainer


@router.post("/", response_model=TrainerSchema)
def create_trainer(trainer: TrainerCreate, db: Session = Depends(get_db)):
    db_trainer = Trainer(**trainer.model_dump())
    db.add(db_trainer)
    db.commit()
    db.refresh(db_trainer)
    return db_trainer


@router.put("/{trainer_id}", response_model=TrainerSchema)
def update_trainer(trainer_id: int, trainer: TrainerCreate, db: Session = Depends(get_db)):
    db_trainer = db.query(Trainer).filter(Trainer.id_trainer == trainer_id).first()
    if db_trainer is None:
        raise HTTPException(status_code=404, detail="Trainer not found")
    for key, value in trainer.model_dump().items():
        setattr(db_trainer, key, value)
    db.commit()
    db.refresh(db_trainer)
    return db_trainer


@router.delete("/{trainer_id}")
def delete_trainer(trainer_id: int, db: Session = Depends(get_db)):
    db_trainer = db.query(Trainer).filter(Trainer.id_trainer == trainer_id).first()
    if db_trainer is None:
        raise HTTPException(status_code=404, detail="Trainer not found")
    db.delete(db_trainer)
    db.commit()
    return {"message": "Trainer deleted"}

