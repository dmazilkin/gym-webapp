from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Date, Time, Enum, Float, TIMESTAMP, Text, DateTime, func
from sqlalchemy.dialects.postgresql import MONEY
from sqlalchemy.orm import relationship
from database import Base
import enum

class WeekDay(enum.Enum):
    Monday = "Monday"
    Tuesday = "Tuesday"
    Wednesday = "Wednesday"
    Thursday = "Thursday"
    Friday = "Friday"
    Saturday = "Saturday"
    Sunday = "Sunday"


class PaymentCurrency(enum.Enum):
    CZK = "CZK"
    EUR = "EUR"


class MembershipStatus(enum.Enum):
    Active = "Active"
    Suspended = "Suspended"
    Cancelled = "Cancelled"


class PaymentStatus(enum.Enum):
    Pending = "Pending"
    Successful = "Successful"
    Failed = "Failed"


class Contact(Base):
    __tablename__ = "contacts"

    id_contact = Column(Integer, primary_key=True, index=True, autoincrement=True)
    phone_number = Column(Text, nullable=False)
    email = Column(Text, nullable=False)

    clients = relationship("Client", back_populates="contact")
    trainers = relationship("Trainer", back_populates="contact")


class Client(Base):
    __tablename__ = "clients"

    id_client = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(20), nullable=False)
    surname = Column(String(20), nullable=False)
    birthday = Column(Date, nullable=False)
    sex = Column(String(1), nullable=False)
    discount = Column(Float, nullable=False)
    id_contact = Column(Integer, ForeignKey("contacts.id_contact"), nullable=False)
    is_admin = Column(Boolean, nullable=False, default=False)

    contact = relationship("Contact", back_populates="clients")
    registrations = relationship("Registered", back_populates="client")
    memberships = relationship("Membership", back_populates="client")
    password = relationship("Password", back_populates="client", uselist=False)
    
class Password(Base):
    __tablename__ = "passwords"

    id_password = Column(Integer, primary_key=True, index=True)
    id_client = Column(Integer, ForeignKey("clients.id_client"), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    client = relationship("Client", back_populates="password")


class Trainer(Base):
    __tablename__ = "trainers"

    id_trainer = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(20), nullable=False)
    surname = Column(String(20), nullable=False)
    birthday = Column(Date, nullable=False)
    sex = Column(String(1), nullable=False)
    id_contact = Column(Integer, ForeignKey("contacts.id_contact"), nullable=False)

    contact = relationship("Contact", back_populates="trainers")
    contracts = relationship("Contract", back_populates="trainer")
    groups = relationship("Group", back_populates="trainer")


class Contract(Base):
    __tablename__ = "contracts"

    id_contract = Column(Integer, primary_key=True, index=True, autoincrement=True)
    salary = Column(Integer, nullable=False)
    contract_type = Column(Text, nullable=False)
    date_from = Column(Date, nullable=False)
    date_to = Column(Date, nullable=False)
    id_trainer = Column(Integer, ForeignKey("trainers.id_trainer"), nullable=False)

    trainer = relationship("Trainer", back_populates="contracts")


class Gym(Base):
    __tablename__ = "gyms"

    id_gym = Column(Integer, primary_key=True, index=True, autoincrement=True)
    country = Column(Text, nullable=False)
    city = Column(Text, nullable=False)
    postcode = Column(Text, nullable=False)
    street = Column(Text, nullable=False)
    building = Column(Text, nullable=False)

    groups = relationship("Group", back_populates="gym")
    opening_hours = relationship("OpeningHours", back_populates="gym")
    memberships = relationship("Membership", back_populates="gym")


class Group(Base):
    __tablename__ = "groups"

    id_group = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_trainer = Column(Integer, ForeignKey("trainers.id_trainer"), nullable=False)
    id_gym = Column(Integer, ForeignKey("gyms.id_gym"), nullable=False)
    max_capacity = Column(Integer, nullable=False)
    time_start = Column(Time, nullable=False)
    time_finish = Column(Time, nullable=False)
    week_day = Column(Enum(WeekDay), nullable=False)

    trainer = relationship("Trainer", back_populates="groups")
    gym = relationship("Gym", back_populates="groups")
    registrations = relationship("Registered", back_populates="group")


class Registered(Base):
    __tablename__ = "registered"

    id_registered = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_group = Column(Integer, ForeignKey("groups.id_group"), nullable=False)
    id_client = Column(Integer, ForeignKey("clients.id_client"), nullable=False)

    group = relationship("Group", back_populates="registrations")
    client = relationship("Client", back_populates="registrations")


class OpeningHours(Base):
    __tablename__ = "opening_hours"

    id_opening_hours = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_gyms = Column(Integer, ForeignKey("gyms.id_gym"))
    week_day = Column(Enum(WeekDay), nullable=False)
    time_open = Column(Time, nullable=False)
    time_close = Column(Time, nullable=False)

    gym = relationship("Gym", back_populates="opening_hours")


class MembershipType(Base):
    __tablename__ = "membership_types"

    id_membership_type = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(Text, nullable=False)
    price = Column(MONEY, nullable=False)
    currency = Column(Enum(PaymentCurrency, name='payment_currency'), nullable=False)
    duration = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)

    memberships = relationship("Membership", back_populates="membership_type")


class Membership(Base):
    __tablename__ = "memberships"

    id_membership = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_client = Column(Integer, ForeignKey("clients.id_client"), nullable=False)
    id_membership_type = Column(Integer, ForeignKey("membership_types.id_membership_type"), nullable=False)
    id_gym = Column(Integer, ForeignKey("gyms.id_gym"), nullable=False)
    membership_status = Column(Enum(MembershipStatus), nullable=False)
    membership_start = Column(Date, nullable=False)
    membership_stop = Column(Date, nullable=False)

    client = relationship("Client", back_populates="memberships")
    membership_type = relationship("MembershipType", back_populates="memberships")
    gym = relationship("Gym", back_populates="memberships")
    payments = relationship("Payment", back_populates="membership")


class Payment(Base):
    __tablename__ = "payments"

    id_payment = Column(Integer, primary_key=True, index=True, autoincrement=True)
    payment_status = Column(Enum(PaymentStatus), nullable=False)
    amount = Column(MONEY, nullable=False)
    currency = Column(Enum(PaymentCurrency, name='payment_currency'), nullable=False)
    date_creation = Column(TIMESTAMP, nullable=False)
    date_payment = Column(TIMESTAMP, nullable=False)
    date_due_date = Column(TIMESTAMP, nullable=False)
    id_membership = Column(Integer, ForeignKey("memberships.id_membership"), nullable=False)

    membership = relationship("Membership", back_populates="payments")

    