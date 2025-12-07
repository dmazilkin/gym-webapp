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

login_router = APIRouter(
    prefix='/auth',
    tags=['auth'],
)

templates = Jinja2Templates(directory=TEMPLATES)

@login_router.get('/login')
async def login_get(request: Request):
    return templates.TemplateResponse('login.html', {'request': request})

@login_router.post('/login')
async def login_post(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    contact = db.query(Contact).filter(Contact.email == form['email']).first()
    
    if not contact:
        login_url = request.url_for('login_get')
        print('contact')
        
        return RedirectResponse(
            f"{login_url}?invalid=1",
            status_code=status.HTTP_303_SEE_OTHER,
        )
        
    client = db.query(Client).filter(Client.id_contact == contact.id_contact).first()
    
    if not client:
        login_url = request.url_for('login_get')
        print('client')
        
        return RedirectResponse(
            f"{login_url}?invalid=1",
            status_code=status.HTTP_303_SEE_OTHER,
        )
        
    pwd = db.query(Password).filter(Password.id_client == client.id_client).first()
    
    if not pwd:
        print('password')
        login_url = request.url_for('login_get')
        
        return RedirectResponse(
            f"{login_url}?invalid=1",
            status_code=status.HTTP_303_SEE_OTHER,
        )
        
    if not verify_password(form['password'], pwd.password_hash):
        login_url = request.url_for('login_get')
        print('verify')
        
        return RedirectResponse(
            f"{login_url}?invalid=1",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    
    if client.is_admin:
        dashboard_url = request.url_for('admin_dashboard_get')
    else:
        dashboard_url = request.url_for('user_dashboard_get')
    
    response = RedirectResponse(dashboard_url, status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key='client_id',
        value=str(client.id_client),
        httponly=True,
        max_age=60*60,
    ) 
    return response