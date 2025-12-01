from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Membership
from schemas import Membership as MembershipSchema, MembershipCreate

router = APIRouter(prefix="/memberships", tags=["memberships"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[MembershipSchema])
def read_memberships(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    memberships = db.query(Membership).offset(skip).limit(limit).all()
    return memberships


@router.get("/{membership_id}", response_model=MembershipSchema)
def read_membership(membership_id: int, db: Session = Depends(get_db)):
    membership = db.query(Membership).filter(Membership.id_membership == membership_id).first()
    if membership is None:
        raise HTTPException(status_code=404, detail="Membership not found")
    return membership


@router.post("/", response_model=MembershipSchema)
def create_membership(membership: MembershipCreate, db: Session = Depends(get_db)):
    db_membership = Membership(**membership.model_dump())
    db.add(db_membership)
    db.commit()
    db.refresh(db_membership)
    return db_membership


@router.put("/{membership_id}", response_model=MembershipSchema)
def update_membership(membership_id: int, membership: MembershipCreate, db: Session = Depends(get_db)):
    db_membership = db.query(Membership).filter(Membership.id_membership == membership_id).first()
    if db_membership is None:
        raise HTTPException(status_code=404, detail="Membership not found")
    for key, value in membership.model_dump().items():
        setattr(db_membership, key, value)
    db.commit()
    db.refresh(db_membership)
    return db_membership


@router.delete("/{membership_id}")
def delete_membership(membership_id: int, db: Session = Depends(get_db)):
    db_membership = db.query(Membership).filter(Membership.id_membership == membership_id).first()
    if db_membership is None:
        raise HTTPException(status_code=404, detail="Membership not found")
    db.delete(db_membership)
    db.commit()
    return {"message": "Membership deleted"}

