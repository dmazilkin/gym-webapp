from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import MembershipType
from schemas import MembershipType as MembershipTypeSchema, MembershipTypeCreate

router = APIRouter(prefix="/membership-types", tags=["membership-types"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[MembershipTypeSchema])
def read_membership_types(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    membership_types = db.query(MembershipType).offset(skip).limit(limit).all()
    return membership_types


@router.get("/{membership_type_id}", response_model=MembershipTypeSchema)
def read_membership_type(membership_type_id: int, db: Session = Depends(get_db)):
    membership_type = db.query(MembershipType).filter(MembershipType.id_membership_type == membership_type_id).first()
    if membership_type is None:
        raise HTTPException(status_code=404, detail="Membership type not found")
    return membership_type


@router.post("/", response_model=MembershipTypeSchema)
def create_membership_type(membership_type: MembershipTypeCreate, db: Session = Depends(get_db)):
    db_membership_type = MembershipType(**membership_type.model_dump())
    db.add(db_membership_type)
    db.commit()
    db.refresh(db_membership_type)
    return db_membership_type


@router.put("/{membership_type_id}", response_model=MembershipTypeSchema)
def update_membership_type(membership_type_id: int, membership_type: MembershipTypeCreate, db: Session = Depends(get_db)):
    db_membership_type = db.query(MembershipType).filter(MembershipType.id_membership_type == membership_type_id).first()
    if db_membership_type is None:
        raise HTTPException(status_code=404, detail="Membership type not found")
    for key, value in membership_type.model_dump().items():
        setattr(db_membership_type, key, value)
    db.commit()
    db.refresh(db_membership_type)
    return db_membership_type


@router.delete("/{membership_type_id}")
def delete_membership_type(membership_type_id: int, db: Session = Depends(get_db)):
    db_membership_type = db.query(MembershipType).filter(MembershipType.id_membership_type == membership_type_id).first()
    if db_membership_type is None:
        raise HTTPException(status_code=404, detail="Membership type not found")
    db.delete(db_membership_type)
    db.commit()
    return {"message": "Membership type deleted"}

