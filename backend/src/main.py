from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from database import engine, Base
from routers import (
    contacts, clients, trainers, contracts, gyms, groups,
    registered, opening_hours, membership_types, memberships, payments
)
from sqlalchemy.orm import Session
from models import Gym, MembershipType, Group, Trainer, Contact, WeekDay
from datetime import date, time

# Create tables
Base.metadata.create_all(bind=engine)

def seed_initial_data():
    db = Session(bind=engine)

    # Seed Gyms
    if db.query(Gym).count() == 0:
        gyms = [
            Gym(country="Czech Republic", city="Brno", postcode="60200", street="Bozetechova", building="1"),
            Gym(country="Czech Republic", city="Prague", postcode="11000", street="Vaclavske nam.", building="10"),
            Gym(country="Slovakia", city="Bratislava", postcode="81101", street="Kapucinska", building="3"),
            Gym(country="Austria", city="Vienna", postcode="1010", street="Stephansplatz", building="5")
        ]
        db.add_all(gyms)

    # Seed Membership Types
    if db.query(MembershipType).count() == 0:
        membership_types = [
            MembershipType(
                title="Monthly Pass",
                price="1000.00",
                currency="CZK",
                duration=date(2025, 2, 28),
                description="Unlimited access for one month."
            ),
            MembershipType(
                title="Quarterly Pass",
                price="2800.00",
                currency="CZK",
                duration=date(2025, 4, 30),
                description="3-month gym access with discount."
            ),
            MembershipType(
                title="Yearly Pass",
                price="9500.00",
                currency="CZK",
                duration=date(2025, 12, 31),
                description="Full-year membership with best price."
            ),
            MembershipType(
                title="Premium Pass",
                price="15000.00",
                currency="CZK",
                duration=date(2025, 12, 31),
                description="Includes unlimited group training & sauna."
            )
        ]
        db.add_all(membership_types)
        
    if db.query(Trainer).count() == 0:
        trainer_contacts = [
            Contact(phone_number="+420111222333", email="trainer1@example.com"),
            Contact(phone_number="+420222333444", email="trainer2@example.com"),
            Contact(phone_number="+420333444555", email="trainer3@example.com"),
        ]
        db.add_all(trainer_contacts)
        db.flush()  # чтобы получить id_contact

        trainers = [
            Trainer(name="Lukas", surname="Novak", birthday=date(1990, 5, 12), sex="M",
                    id_contact=trainer_contacts[0].id_contact),
            Trainer(name="Petra", surname="Svobodova", birthday=date(1988, 11, 3), sex="F",
                    id_contact=trainer_contacts[1].id_contact),
            Trainer(name="Tomas", surname="Kral", birthday=date(1995, 2, 25), sex="M",
                    id_contact=trainer_contacts[2].id_contact),
        ]
        db.add_all(trainers)
        
    if db.query(Group).count() == 0:
        all_trainers = db.query(Trainer).all()
        all_gyms = db.query(Gym).all()

        if all_trainers and all_gyms:
            groups = [
                Group(
                    id_trainer=all_trainers[0].id_trainer,
                    id_gym=all_gyms[0].id_gym,
                    max_capacity=20,
                    time_start=time(9, 0),
                    time_finish=time(10, 0),
                    week_day=WeekDay.MONDAY,      # <<< ВАЖНО
                ),
                Group(
                    id_trainer=all_trainers[1].id_trainer,
                    id_gym=all_gyms[1].id_gym,
                    max_capacity=15,
                    time_start=time(17, 0),
                    time_finish=time(18, 30),
                    week_day=WeekDay.WEDNESDAY,   # <<< НЕ .name, НЕ "WEDNESDAY"
                ),
                Group(
                    id_trainer=all_trainers[2].id_trainer,
                    id_gym=all_gyms[2].id_gym,
                    max_capacity=25,
                    time_start=time(19, 0),
                    time_finish=time(20, 0),
                    week_day=WeekDay.FRIDAY,
                ),
                Group(
                    id_trainer=all_trainers[0].id_trainer,
                    id_gym=all_gyms[3].id_gym,
                    max_capacity=30,
                    time_start=time(14, 0),
                    time_finish=time(15, 30),
                    week_day=WeekDay.SATURDAY,
                ),
            ]
            db.add_all(groups)

    db.commit()
    db.close()

# Call seeding
seed_initial_data()

app = FastAPI(title="Gym Management API", version="1.0.0")

# Configure CORS - allow all origins since we're serving frontend from the same server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers FIRST (before root route)
app.include_router(contacts.router)
app.include_router(clients.router)
app.include_router(trainers.router)
app.include_router(contracts.router)
app.include_router(gyms.router)
app.include_router(groups.router)
app.include_router(registered.router)
app.include_router(opening_hours.router)
app.include_router(membership_types.router)
app.include_router(memberships.router)
app.include_router(payments.router)

# Get path to frontend directory
frontend_path = Path(__file__).parent.parent.parent / "frontend"

# Mount static files (CSS, JS)
app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

# Serve frontend files - this should be LAST to catch all other routes
@app.get("/")
async def read_root():
    """Serve the frontend index.html"""
    index_path = frontend_path / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "Gym Management API", "docs": "/docs", "frontend": "Frontend files not found"}




@app.get("/favicon.ico")
def favicon():
    from fastapi.responses import Response
    return Response(status_code=204)  # No Content

