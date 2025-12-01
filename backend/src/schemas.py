from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, time, datetime
from models import WeekDay, PaymentCurrency, MembershipStatus, PaymentStatus


# Contact schemas
class ContactBase(BaseModel):
    phone_number: str
    email: str


class ContactCreate(ContactBase):
    pass


class Contact(ContactBase):
    id_contact: int

    class Config:
        from_attributes = True


# Client schemas
class ClientBase(BaseModel):
    name: str
    surname: str
    birthday: date
    sex: str
    id_contact: int


class ClientCreate(ClientBase):
    pass


class Client(ClientBase):
    id_client: int

    class Config:
        from_attributes = True


# Trainer schemas
class TrainerBase(BaseModel):
    name: str
    surname: str
    birthday: date
    sex: str
    id_contact: int


class TrainerCreate(TrainerBase):
    pass


class Trainer(TrainerBase):
    id_trainer: int

    class Config:
        from_attributes = True


# Contract schemas
class ContractBase(BaseModel):
    salary: int
    contract_type: str
    date_from: date
    date_to: date
    id_trainer: int


class ContractCreate(ContractBase):
    pass


class Contract(ContractBase):
    id_contract: int

    class Config:
        from_attributes = True


# Gym schemas
class GymBase(BaseModel):
    country: str
    city: str
    postcode: str
    street: str
    building: str


class GymCreate(GymBase):
    pass


class Gym(GymBase):
    id_gym: int

    class Config:
        from_attributes = True


# Group schemas
class GroupBase(BaseModel):
    id_trainer: int
    id_gym: int
    max_capacity: int
    time_start: time
    time_finish: time
    week_day: WeekDay


class GroupCreate(GroupBase):
    pass


class Group(GroupBase):
    id_group: int

    class Config:
        from_attributes = True


# Registered schemas
class RegisteredBase(BaseModel):
    id_group: int
    id_client: int


class RegisteredCreate(RegisteredBase):
    pass


class Registered(RegisteredBase):
    id_registered: int

    class Config:
        from_attributes = True


# OpeningHours schemas
class OpeningHoursBase(BaseModel):
    id_gyms: Optional[int] = None
    week_day: WeekDay
    time_open: time
    time_close: time


class OpeningHoursCreate(OpeningHoursBase):
    pass


class OpeningHours(OpeningHoursBase):
    id_opening_hours: int

    class Config:
        from_attributes = True


# MembershipType schemas
class MembershipTypeBase(BaseModel):
    title: str
    price: str  # MONEY type as string
    currency: PaymentCurrency
    duration: date
    description: str


class MembershipTypeCreate(MembershipTypeBase):
    pass


class MembershipType(MembershipTypeBase):
    id_membership_type: int

    class Config:
        from_attributes = True


# Membership schemas
class MembershipBase(BaseModel):
    id_client: int
    id_membership_type: int
    id_gym: int
    membership_status: MembershipStatus
    discount: float
    membership_start: date
    membership_stop: date


class MembershipCreate(MembershipBase):
    pass


class Membership(MembershipBase):
    id_membership: int

    class Config:
        from_attributes = True


# Payment schemas
class PaymentBase(BaseModel):
    payment_status: PaymentStatus
    amount: str  # MONEY type as string
    currency: PaymentCurrency
    date_creation: datetime
    date_payment: datetime
    date_due_date: datetime
    id_membership: int


class PaymentCreate(PaymentBase):
    pass


class Payment(PaymentBase):
    id_payment: int

    class Config:
        from_attributes = True

