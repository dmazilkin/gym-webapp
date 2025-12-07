from fastapi import APIRouter, HTTPException, Request, Depends, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from config import TEMPLATES
from database import get_db
from models import Contact, Client, MembershipStatus, Membership, MembershipType, Gym, PaymentCurrency, Payment
from security import get_current_user

from datetime import date

LIMIT_USERS_COUNT = 5
MAX_HISTORY = 5


admin_router = APIRouter(
    prefix='/admin',
    tags=['admin'],
)

templates = Jinja2Templates(directory=TEMPLATES)

@admin_router.get("/dashboard", response_class=HTMLResponse, name='admin_dashboard_get')
async def admin_dashboard_get(
    request: Request,
    db: Session = Depends(get_db),
    admin: Client = Depends(get_current_user),
    name: str | None = None,
    surname: str | None = None,
    phone: str | None = None,
    email: str | None = None,
    admins_only: bool = False,
    selected: int | None = None,
):

    if not admin.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    no_filters = not any([name, surname, phone, email, admins_only])

    if no_filters:
        clients = None
    else:
        clients_query = db.query(Client).join(Contact)

        if name:
            clients_query = clients_query.filter(Client.name.ilike(f"%{name}%"))
        if surname:
            clients_query = clients_query.filter(Client.surname.ilike(f"%{surname}%"))
        if phone:
            clients_query = clients_query.filter(Contact.phone_number.ilike(f"%{phone}%"))
        if email:
            clients_query = clients_query.filter(Contact.email.ilike(f"%{email}%"))

        if admins_only:
            clients_query = clients_query.filter(Client.is_admin == True)

        clients = (
            clients_query
            .order_by(Client.surname, Client.name)
            .limit(LIMIT_USERS_COUNT)
            .all()
        )

    selected_client = None
    if selected:
        selected_client = (
            db.query(Client)
            .join(Contact)
            .filter(Client.id_client == selected)
            .first()
        )

    return templates.TemplateResponse(
        "admin_dashboard.html",
        {
            "request": request,
            "admin": admin,
            "admins_only": admins_only,
            "clients": clients,
            "name": name,
            "surname": surname,
            "phone": phone,
            "email": email,
            "selected_client": selected_client,
        },
        status_code=200,
    )

@admin_router.post("/toggle-admin/{client_id}", name="admin_toggle_admin_post")
async def admin_toggle_admin_post(
    client_id: int,
    db: Session = Depends(get_db),
    admin: Client = Depends(get_current_user),
):

    if not admin.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    target = db.query(Client).filter(Client.id_client == client_id).first()

    if not target:
        raise HTTPException(status_code=404, detail="Client not found")

    if target.id_client == admin.id_client:
        raise HTTPException(status_code=400, detail="Admin cannot remove himself")

    target.is_admin = not target.is_admin
    db.commit()

    return RedirectResponse(
        f"/admin/dashboard?selected={client_id}",
        status_code=303
    )

@admin_router.get("/clients/{client_id}", response_class=HTMLResponse, name="admin_client_detail_get")
async def admin_client_details_get(
    client_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: Client = Depends(get_current_user),
):
    if not admin.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    client = (
        db.query(Client)
        .filter(Client.id_client == client_id)
        .first()
    )
    if not client:
        return RedirectResponse(
            url=request.url_for("admin_dashboard_get"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    active_membership = None
    for m in client.memberships:
        if m.membership_status == MembershipStatus.Active:
            active_membership = m
            break

    membership_history = sorted(
        client.memberships,
        key=lambda m: m.membership_start,
        reverse=False,
    )[-MAX_HISTORY:]

    last_payment_by_membership: dict[int, Payment] = {}
    for m in client.memberships:
        if m.payments:
            last_payment = sorted(
                m.payments,
                key=lambda p: p.date_payment or p.date_creation
            )[-1]
            last_payment_by_membership[m.id_membership] = last_payment

    return templates.TemplateResponse(
        "admin_client_detail.html",
        {
            "request": request,
            "admin": admin,
            "client": client,
            "active_membership": active_membership,
            "membership_history": membership_history,
            "last_payment_by_membership": last_payment_by_membership,
        },
        status_code=200,
    )

@admin_router.post(
    "/clients/{client_id}/discount",
    name="admin_update_discount_post",
)
async def admin_update_discount_post(
    client_id: int,
    request: Request,
    discount: float = Form(...),
    db: Session = Depends(get_db),
    admin: Client = Depends(get_current_user),
):
    if not admin.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    client = (
        db.query(Client)
        .filter(Client.id_client == client_id)
        .first()
    )
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    if not (0 <= discount <= 100):
        raise HTTPException(status_code=400, detail="Discount must be between 0 and 100")

    client.discount = discount

    db.commit()

    return RedirectResponse(
        url=request.url_for("admin_client_detail_get", client_id=client_id),
        status_code=status.HTTP_303_SEE_OTHER,
    )



@admin_router.get(
    "/membership-types",
    response_class=HTMLResponse,
    name="admin_membership_types_get",
)
async def admin_membership_types_get(
    request: Request,
    db: Session = Depends(get_db),
    admin: Client = Depends(get_current_user),
):
    if not admin.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    membership_types = (
        db.query(MembershipType)
        .order_by(MembershipType.title)
        .all()
    )

    return templates.TemplateResponse(
        "admin_membership_types.html",
        {
            "request": request,
            "admin": admin,
            "membership_types": membership_types,
        },
        status_code=200,
    )


@admin_router.post(
    "/membership-types",
    name="admin_membership_type_create_post",
)
async def admin_membership_type_create_post(
    title: str = Form(...),
    price: str = Form(...),
    currency: str = Form(...),
    duration: int = Form(...),
    description: str = Form(...),
    db: Session = Depends(get_db),
    admin: Client = Depends(get_current_user),
):
    if not admin.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    mt = MembershipType(
        title=title,
        price=price,
        currency=PaymentCurrency(currency),
        duration=duration,
        description=description,
    )
    db.add(mt)
    db.commit()

    return RedirectResponse(
        url="/admin/membership-types",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@admin_router.get(
    "/membership-types/{membership_type_id}/edit",
    response_class=HTMLResponse,
    name="admin_membership_type_edit_get",
)
async def admin_membership_type_edit_get(
    membership_type_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: Client = Depends(get_current_user),
):
    if not admin.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    membership_type = (
        db.query(MembershipType)
        .filter(MembershipType.id_membership_type == membership_type_id)
        .first()
    )
    if not membership_type:
        raise HTTPException(status_code=404, detail="Membership type not found")

    return templates.TemplateResponse(
        "admin_membership_type_edit.html",
        {
            "request": request,
            "admin": admin,
            "membership_type": membership_type,
        },
        status_code=200,
    )


@admin_router.post(
    "/membership-types/{membership_type_id}/edit",
    name="admin_membership_type_edit_post",
)
async def admin_membership_type_edit_post(
    membership_type_id: int,
    title: str = Form(...),
    price: str = Form(...),
    currency: str = Form(...),
    duration: int = Form(...),
    description: str = Form(...),
    db: Session = Depends(get_db),
    admin: Client = Depends(get_current_user),
):
    if not admin.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    membership_type = (
        db.query(MembershipType)
        .filter(MembershipType.id_membership_type == membership_type_id)
        .first()
    )
    if not membership_type:
        raise HTTPException(status_code=404, detail="Membership type not found")

    membership_type.title = title
    membership_type.price = price
    membership_type.currency = PaymentCurrency(currency)
    membership_type.duration = duration
    membership_type.description = description

    db.commit()

    return RedirectResponse(
        url="/admin/membership-types",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@admin_router.post(
    "/membership-types/{membership_type_id}/delete",
    name="admin_membership_type_delete_post",
)
async def admin_membership_type_delete_post(
    membership_type_id: int,
    db: Session = Depends(get_db),
    admin: Client = Depends(get_current_user),
):
    if not admin.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    membership_type = (
        db.query(MembershipType)
        .filter(MembershipType.id_membership_type == membership_type_id)
        .first()
    )
    if not membership_type:
        raise HTTPException(status_code=404, detail="Membership type not found")

    db.delete(membership_type)
    db.commit()

    return RedirectResponse(
        url="/admin/membership-types",
        status_code=status.HTTP_303_SEE_OTHER,
    )

@admin_router.get(
    "/gyms",
    response_class=HTMLResponse,
    name="admin_gyms_get",
)
async def admin_gyms_get(
    request: Request,
    db: Session = Depends(get_db),
    admin: Client = Depends(get_current_user),
):
    if not admin.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    gyms = (
        db.query(Gym)
        .order_by(Gym.city, Gym.street, Gym.building)
        .all()
    )

    return templates.TemplateResponse(
        "admin_gyms.html",
        {
            "request": request,
            "admin": admin,
            "gyms": gyms,
        },
        status_code=200,
    )


@admin_router.post(
    "/gyms",
    name="admin_gym_create_post",
)
async def admin_gym_create_post(
    country: str = Form(...),
    city: str = Form(...),
    postcode: str = Form(...),
    street: str = Form(...),
    building: str = Form(...),
    db: Session = Depends(get_db),
    admin: Client = Depends(get_current_user),
):
    if not admin.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    gym = Gym(
        country=country,
        city=city,
        postcode=postcode,
        street=street,
        building=building,
    )
    db.add(gym)
    db.commit()

    return RedirectResponse(
        url="/admin/gyms",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@admin_router.get(
    "/gyms/{gym_id}/edit",
    response_class=HTMLResponse,
    name="admin_gym_edit_get",
)
async def admin_gym_edit_get(
    gym_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: Client = Depends(get_current_user),
):
    if not admin.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    gym = (
        db.query(Gym)
        .filter(Gym.id_gym == gym_id)
        .first()
    )
    if not gym:
        raise HTTPException(status_code=404, detail="Gym not found")

    return templates.TemplateResponse(
        "admin_gym_edit.html",
        {
            "request": request,
            "admin": admin,
            "gym": gym,
        },
        status_code=200,
    )


@admin_router.post(
    "/gyms/{gym_id}/edit",
    name="admin_gym_edit_post",
)
async def admin_gym_edit_post(
    gym_id: int,
    country: str = Form(...),
    city: str = Form(...),
    postcode: str = Form(...),
    street: str = Form(...),
    building: str = Form(...),
    db: Session = Depends(get_db),
    admin: Client = Depends(get_current_user),
):
    if not admin.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    gym = (
        db.query(Gym)
        .filter(Gym.id_gym == gym_id)
        .first()
    )
    if not gym:
        raise HTTPException(status_code=404, detail="Gym not found")

    gym.country = country
    gym.city = city
    gym.postcode = postcode
    gym.street = street
    gym.building = building

    db.commit()

    return RedirectResponse(
        url="/admin/gyms",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@admin_router.post(
    "/gyms/{gym_id}/delete",
    name="admin_gym_delete_post",
)
async def admin_gym_delete_post(
    gym_id: int,
    db: Session = Depends(get_db),
    admin: Client = Depends(get_current_user),
):
    if not admin.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    gym = (
        db.query(Gym)
        .filter(Gym.id_gym == gym_id)
        .first()
    )
    if not gym:
        raise HTTPException(status_code=404, detail="Gym not found")

    db.delete(gym)
    db.commit()

    return RedirectResponse(
        url="/admin/gyms",
        status_code=status.HTTP_303_SEE_OTHER,
    )
