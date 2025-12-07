from passlib.context import CryptContext
from fastapi import Request, HTTPException, status, Depends

from database import get_db
from models import Client

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
)

def hash_password(password: str) -> str:
    if password is None:
        password = ""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if plain_password is None:
        plain_password = ""
    return pwd_context.verify(plain_password, hashed_password)

def get_current_user(request: Request, db=Depends(get_db)):
    client_id = request.cookies.get("client_id")
    if not client_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = db.query(Client).filter(Client.id_client == int(client_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Unknown session")

    return user


