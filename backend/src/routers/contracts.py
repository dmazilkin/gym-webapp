from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Contract
from schemas import Contract as ContractSchema, ContractCreate

router = APIRouter(prefix="/contracts", tags=["contracts"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[ContractSchema])
def read_contracts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    contracts = db.query(Contract).offset(skip).limit(limit).all()
    return contracts


@router.get("/{contract_id}", response_model=ContractSchema)
def read_contract(contract_id: int, db: Session = Depends(get_db)):
    contract = db.query(Contract).filter(Contract.id_contract == contract_id).first()
    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract


@router.post("/", response_model=ContractSchema)
def create_contract(contract: ContractCreate, db: Session = Depends(get_db)):
    db_contract = Contract(**contract.model_dump())
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    return db_contract


@router.put("/{contract_id}", response_model=ContractSchema)
def update_contract(contract_id: int, contract: ContractCreate, db: Session = Depends(get_db)):
    db_contract = db.query(Contract).filter(Contract.id_contract == contract_id).first()
    if db_contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")
    for key, value in contract.model_dump().items():
        setattr(db_contract, key, value)
    db.commit()
    db.refresh(db_contract)
    return db_contract


@router.delete("/{contract_id}")
def delete_contract(contract_id: int, db: Session = Depends(get_db)):
    db_contract = db.query(Contract).filter(Contract.id_contract == contract_id).first()
    if db_contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")
    db.delete(db_contract)
    db.commit()
    return {"message": "Contract deleted"}

