from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Group
from schemas import Group as GroupSchema, GroupCreate

router = APIRouter(prefix="/groups", tags=["groups"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[GroupSchema])
def read_groups(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    groups = db.query(Group).offset(skip).limit(limit).all()
    return groups


@router.get("/{group_id}", response_model=GroupSchema)
def read_group(group_id: int, db: Session = Depends(get_db)):
    group = db.query(Group).filter(Group.id_group == group_id).first()
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return group


@router.post("/", response_model=GroupSchema)
def create_group(group: GroupCreate, db: Session = Depends(get_db)):
    db_group = Group(**group.model_dump())
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group


@router.put("/{group_id}", response_model=GroupSchema)
def update_group(group_id: int, group: GroupCreate, db: Session = Depends(get_db)):
    db_group = db.query(Group).filter(Group.id_group == group_id).first()
    if db_group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    for key, value in group.model_dump().items():
        setattr(db_group, key, value)
    db.commit()
    db.refresh(db_group)
    return db_group


@router.delete("/{group_id}")
def delete_group(group_id: int, db: Session = Depends(get_db)):
    db_group = db.query(Group).filter(Group.id_group == group_id).first()
    if db_group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    db.delete(db_group)
    db.commit()
    return {"message": "Group deleted"}

