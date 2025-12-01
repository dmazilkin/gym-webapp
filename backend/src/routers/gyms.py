from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Gym
from schemas import Gym as GymSchema, GymCreate

router = APIRouter(prefix="/gyms", tags=["gyms"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[GymSchema])
def read_gyms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    gyms = db.query(Gym).offset(skip).limit(limit).all()
    return gyms


@router.get("/{gym_id}", response_model=GymSchema)
def read_gym(gym_id: int, db: Session = Depends(get_db)):
    gym = db.query(Gym).filter(Gym.id_gym == gym_id).first()
    if gym is None:
        raise HTTPException(status_code=404, detail="Gym not found")
    return gym


@router.post("/", response_model=GymSchema)
def create_gym(gym: GymCreate, db: Session = Depends(get_db)):
    db_gym = Gym(**gym.model_dump())
    db.add(db_gym)
    db.commit()
    db.refresh(db_gym)
    return db_gym


@router.put("/{gym_id}", response_model=GymSchema)
def update_gym(gym_id: int, gym: GymCreate, db: Session = Depends(get_db)):
    db_gym = db.query(Gym).filter(Gym.id_gym == gym_id).first()
    if db_gym is None:
        raise HTTPException(status_code=404, detail="Gym not found")
    for key, value in gym.model_dump().items():
        setattr(db_gym, key, value)
    db.commit()
    db.refresh(db_gym)
    return db_gym


@router.delete("/{gym_id}")
def delete_gym(gym_id: int, db: Session = Depends(get_db)):
    db_gym = db.query(Gym).filter(Gym.id_gym == gym_id).first()
    if db_gym is None:
        raise HTTPException(status_code=404, detail="Gym not found")
    db.delete(db_gym)
    db.commit()
    return {"message": "Gym deleted"}

