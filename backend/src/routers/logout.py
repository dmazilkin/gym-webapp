import http
from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_

from security import verify_password
from config import TEMPLATES
from database import get_db
from models import Contact, Client, Password

logout_router = APIRouter(
    prefix='/auth',
    tags=['auth'],
)

templates = Jinja2Templates(directory=TEMPLATES)

@logout_router.post('/logout', name='logout_post')
async def logout_post(request: Request):
    login_url = request.url_for("login_get")
    response = RedirectResponse(login_url, status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("client_id")
    
    return response