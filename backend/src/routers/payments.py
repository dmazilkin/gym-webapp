from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Payment
from schemas import Payment as PaymentSchema, PaymentCreate

router = APIRouter(prefix="/payments", tags=["payments"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[PaymentSchema])
def read_payments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    payments = db.query(Payment).offset(skip).limit(limit).all()
    return payments


@router.get("/{payment_id}", response_model=PaymentSchema)
def read_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id_payment == payment_id).first()
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.post("/", response_model=PaymentSchema)
def create_payment(payment: PaymentCreate, db: Session = Depends(get_db)):
    db_payment = Payment(**payment.model_dump())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment


@router.put("/{payment_id}", response_model=PaymentSchema)
def update_payment(payment_id: int, payment: PaymentCreate, db: Session = Depends(get_db)):
    db_payment = db.query(Payment).filter(Payment.id_payment == payment_id).first()
    if db_payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    for key, value in payment.model_dump().items():
        setattr(db_payment, key, value)
    db.commit()
    db.refresh(db_payment)
    return db_payment


@router.delete("/{payment_id}")
def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    db_payment = db.query(Payment).filter(Payment.id_payment == payment_id).first()
    if db_payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    db.delete(db_payment)
    db.commit()
    return {"message": "Payment deleted"}

