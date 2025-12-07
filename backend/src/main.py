from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import date, timedelta

from config import STYLES
from routers.register import register_router
from routers.login import login_router
from routers.user import user_router
from routers.admin import admin_router
from routers.logout import logout_router
from security import hash_password
from database import SessionLocal
from models import Client, Contact, Password, MembershipType, Gym, Group

@asynccontextmanager
async def lifespan(app: FastAPI):
    db: Session = SessionLocal()
    try:
        admin_exists = db.query(Client).filter(Client.is_admin == True).first()

        if not admin_exists:
            admin_contact = Contact(
                email='admin@gym.local',
                phone_number='+420000000000'
            )
            
            db.add(admin_contact)
            db.flush()
            
            admin = Client(
                name='Admin',
                surname='Admin',
                birthday=date.today(),
                sex='M',
                discount=0.0,
                id_contact=admin_contact.id_contact,
                is_admin=True
            )
            
            db.add(admin)
            db.flush()
            
            admin_password = Password(
                id_client = admin.id_client,
                password_hash=hash_password('admin123'),
            )
            
            db.add(admin_password)
            db.commit()
            
        has_membership_types = db.query(MembershipType).first()
            
        today = date.today()
            
        if not has_membership_types:
            basic = MembershipType(
                title='Basic 1 month',
                price=300,
                currency='CZK',
                duration=30,
                description='Basic access to the gym for 1 month.',
            )
            standard = MembershipType(
                title='Standard 1 month',
                price=500,
                currency='CZK',
                duration=30,
                description='Standard membership with extended hours.',
            )
            premium = MembershipType(
                title='Premium 1 month',
                price=800,
                currency='CZK',
                duration=30,
                description='Premium membership with all-day access and group classes.',
            )
            db.add_all([basic, standard, premium])
            db.commit()
                
        has_gyms = db.query(Gym).first()
        
        if not has_gyms:
            gym1 = Gym(
                country='Czechia',
                city='Brno',
                postcode ='60200',
                street='Ceska',
                building='1',
            )
            gym2 = Gym(
                country='Czechia',
                city='Brno',
                postcode='61200',
                street='Kolejni',
                building="2",
            )
            db.add_all([gym1, gym2])
            db.commit()
            
    finally:
        db.close()
    
    yield

app = FastAPI(lifespan=lifespan)

app.mount('/css', StaticFiles(directory=STYLES), name='css')
app.include_router(register_router)
app.include_router(login_router)
app.include_router(logout_router)
app.include_router(user_router)
app.include_router(admin_router)

@app.get('/')
async def root():
    return {"message": "Hello World"}