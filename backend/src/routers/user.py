from fastapi import APIRouter, Request, Depends, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import date, timedelta
from decimal import Decimal

from config import TEMPLATES
from database import get_db
from security import get_current_user
from models import Payment, Client, MembershipStatus, MembershipType, Gym, Group, Membership, PaymentStatus, Registered

MAX_HISTORY = 5

user_router = APIRouter(
    prefix='/user',
    tags=['user'],
)

templates = Jinja2Templates(directory=TEMPLATES)

def parse_money(value) -> Decimal:
    raw = str(value)

    cleaned = (
        raw.replace('$', '')
           .replace('€', '')
           .replace('£', '')
           .replace('Kč', '')
           .replace('CZK', '')
           .replace(',', '')
           .strip()
    )

    return Decimal(cleaned)
    
@user_router.get("/dashboard", response_class=HTMLResponse, name='user_dashboard_get')
async def user_dashboard_get(
    request: Request,
    db: Session = Depends(get_db),
    user: Client = Depends(get_current_user),
):
    active_membership = None
    for m in user.memberships:
        if m.membership_status == MembershipStatus.Active:
            active_membership = m
            break

    membership_history = sorted(
        user.memberships,
        key=lambda m: m.membership_start,
        reverse=False,
    )[-MAX_HISTORY:]


    membership_types = db.query(MembershipType).all()
    gyms = db.query(Gym).all()
    groups = db.query(Group).all()

    registered_group_ids = {r.id_group for r in user.registrations}

    return templates.TemplateResponse(
        "user_dashboard.html",
        {
            "request": request,
            "client": user,
            "active_membership": active_membership,
            "membership_history": membership_history,
            "membership_types": membership_types,
            "gyms": gyms,
            "groups": groups,
            "registered_group_ids": registered_group_ids,
        },
        status_code=200,
    )

@user_router.post(
    "/membership/buy",
    response_class=HTMLResponse,
    name="user_membership_buy_post",
)
async def user_membership_buy_post(
    request: Request,
    membership_type_id: int = Form(...),
    gym_id: int = Form(...),
    db: Session = Depends(get_db),
    user: Client = Depends(get_current_user),
):
    mtype = (
        db.query(MembershipType)
        .filter(MembershipType.id_membership_type == membership_type_id)
        .first()
    )

    gym = db.query(Gym).filter(Gym.id_gym == gym_id).first()

    if not mtype or not gym:
        return RedirectResponse(
            url=request.url_for("user_dashboard_get"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    existing_active = (
        db.query(Membership)
        .filter(
            Membership.id_client == user.id_client,
            Membership.membership_status == MembershipStatus.Active,
        )
        .first()
    )

    if existing_active:
        redirect_url = request.url_for("user_dashboard_get").include_query_params(
            has_active="1"
        )
        return RedirectResponse(
            url=redirect_url,
            status_code=status.HTTP_303_SEE_OTHER,
        )

    personal_discount = Decimal(str(user.discount or 0))
    base_price = parse_money(mtype.price) 

    final_price = base_price * (Decimal("1") - personal_discount / Decimal("100"))

    start = date.today()
    stop = start + timedelta(days=mtype.duration)

    new_membership = Membership(
        id_client=user.id_client,
        id_membership_type=mtype.id_membership_type,
        id_gym=gym.id_gym,
        membership_status=MembershipStatus.Active,
        membership_start=start,
        membership_stop=stop,
    )

    db.add(new_membership)
    db.flush() 

    payment = Payment(
        id_membership=new_membership.id_membership,
        payment_status='Successful',
        amount=final_price,        
        currency=mtype.currency,
        date_creation=date.today(),
        date_payment=date.today(),
        date_due_date=date.today(),
    )
    db.add(payment)

    db.commit()

    return RedirectResponse(
        url=request.url_for("user_dashboard_get"),
        status_code=status.HTTP_303_SEE_OTHER,
    )
            
@user_router.post(
    "/membership/cancel",
    response_class=HTMLResponse,
    name="user_membership_cancel_post",
)
async def user_membership_cancel_post(
    request: Request,
    membership_id: int = Form(...),
    db: Session = Depends(get_db),
    user: Client = Depends(get_current_user),
):
    membership = (
        db.query(Membership)
        .filter(
            Membership.id_membership == membership_id,
            Membership.id_client == user.id_client,
        )
        .first()
    )

    if membership:
        membership.membership_status = MembershipStatus.Cancelled
        db.commit()

    return RedirectResponse(
        url=request.url_for("user_dashboard_get"),
        status_code=status.HTTP_303_SEE_OTHER,
    )

@user_router.post(
    "/groups/register",
    response_class=HTMLResponse,
    name="user_group_register_post",
)
async def user_group_register_post(
    request: Request,
    group_id: int = Form(...),
    db: Session = Depends(get_db),
    user: Client = Depends(get_current_user),
):
    group = db.query(Group).filter(Group.id_group == group_id).first()
    if not group:
        return RedirectResponse(
            url=request.url_for("user_dashboard_get"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    already = (
        db.query(Registered)
        .filter(
            Registered.id_group == group.id_group,
            Registered.id_client == user.id_client,
        )
        .first()
    )
    if already:
        return RedirectResponse(
            url=request.url_for("user_dashboard_get"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    current_count = db.query(Registered).filter(
        Registered.id_group == group.id_group
    ).count()
    if current_count >= group.max_capacity:
        return RedirectResponse(
            url=request.url_for("user_dashboard_get"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    registration = Registered(
        id_group=group.id_group,
        id_client=user.id_client,
    )
    db.add(registration)
    db.commit()

    return RedirectResponse(
        url=request.url_for("user_dashboard_get"),
        status_code=status.HTTP_303_SEE_OTHER,
    )