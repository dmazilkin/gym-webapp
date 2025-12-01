from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Client
from schemas import Client as ClientSchema, ClientCreate

router = APIRouter(prefix="/clients", tags=["clients"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[ClientSchema])
def read_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    clients = db.query(Client).offset(skip).limit(limit).all()
    return clients


@router.get("/{client_id}", response_model=ClientSchema)
def read_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id_client == client_id).first()
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.post("/", response_model=ClientSchema)
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    db_client = Client(**client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


@router.put("/{client_id}", response_model=ClientSchema)
def update_client(client_id: int, client: ClientCreate, db: Session = Depends(get_db)):
    db_client = db.query(Client).filter(Client.id_client == client_id).first()
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    for key, value in client.model_dump().items():
        setattr(db_client, key, value)
    db.commit()
    db.refresh(db_client)
    return db_client


@router.delete("/{client_id}")
def delete_client(client_id: int, db: Session = Depends(get_db)):
    db_client = db.query(Client).filter(Client.id_client == client_id).first()
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    db.delete(db_client)
    db.commit()
    return {"message": "Client deleted"}

