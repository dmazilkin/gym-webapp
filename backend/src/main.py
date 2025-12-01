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

# Create tables
# Note: If tables already exist with wrong schema, you may need to drop them first:
# Base.metadata.drop_all(bind=engine)  # Uncomment this line once to recreate tables
Base.metadata.create_all(bind=engine)

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

