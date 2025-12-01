from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "postgresql+psycopg://gym_user:123@localhost:5432/gym_db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
