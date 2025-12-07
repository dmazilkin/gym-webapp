from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_

from config import TEMPLATES
from database import get_db
from models import Contact, Client, Password
from security import hash_password

register_router = APIRouter(
    prefix='/auth',
    tags=['auth'],
)

sex_map = {
    'male': 'M',
    'female': 'F',
    'other': 'O',
}

templates = Jinja2Templates(directory=TEMPLATES)

@register_router.get('/register', response_class=HTMLResponse)
async def register_get(request: Request) -> HTMLResponse:
    return templates.TemplateResponse('register.html', {'request': request}, status_code=200)

@register_router.post('/register')
async def register_post(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    form = await request.form()
    
    from datetime import datetime

    phone = form["phone_number"].strip()
    
    if phone.startswith("+"):
        digits = phone[1:]
    else:
        digits = phone

    if not digits.isdigit():
        register_url = request.url_for('register_get')
        
        return RedirectResponse(
            url=f"{register_url}?phone_invalid=1",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    if not (9 <= len(phone) <= 15):
        register_url = request.url_for('register_get')

        return RedirectResponse(
            url=f"{register_url}?phone_length=1",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    birth_date_raw = form["birth_date"].strip()

    try:
        birth_date = datetime.strptime(birth_date_raw, "%Y-%m-%d").date()

        if not (1900 <= birth_date.year <= 2025):
            raise ValueError

    except ValueError:
        register_url = request.url_for('register_get')
        return RedirectResponse(
            url=f"{register_url}?date_invalid=1",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    
    if form['password'] != form['password_confirm']:
        register_url = request.url_for('register_get')
        return RedirectResponse(
            url=f'{register_url}?pwd_mismatch=1',
            status_code=status.HTTP_303_SEE_OTHER,
        )
    
    is_user_exist = db.query(Contact).filter(
        or_(
            Contact.phone_number == form['phone_number'],
            Contact.email == form['email']
        )
    ).count() > 0
    
    if is_user_exist:
        register_url = request.url_for('register_get')
        return RedirectResponse(
            url=f"{register_url}?exists=1",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    
    new_contact = Contact(
            phone_number=form['phone_number'],
            email=form['email'],
        )
    
    db.add(new_contact)
    db.flush()
    
    new_client = Client(
        name=form['name'],
        surname=form['surname'],
        birthday=form['birth_date'],
        sex=sex_map[form['sex']],
        discount=0.0,
        id_contact=new_contact.id_contact,
    )
    
    db.add(new_client)
    
    db.flush()
    
    new_password = Password(
        id_client=new_client.id_client,
        password_hash=hash_password(form['password']),
    )
    
    db.add(new_password)
    db.commit()
    
    login_url = request.url_for('login_get')
    
    return RedirectResponse(
        url=login_url,
        status_code=status.HTTP_303_SEE_OTHER,
    )
