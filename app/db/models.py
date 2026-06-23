# 📦 Standard library
from sqlalchemy import DateTime
from datetime import datetime

# 🌐 Third-party
from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship

# 📁 Local imports
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role =Column(String)

    terms_accepted = Column(Boolean, default=False)
    terms_accepted_at = Column(DateTime, nullable=True)
    terms_version = Column(String, nullable=True)

    created_at = Column(DateTime,default=datetime.now,nullable=False)

    clients = relationship(
        "Client",
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer,primary_key=True,index=True,)

    first_name = Column(String,nullable=False,)

    last_name = Column(String,nullable=False,)

    phone = Column(String, index=True, nullable=False)

    address = Column(String,nullable=True,)

    notes = Column(String,nullable=True,)

    loyalty_points = Column(Integer,default=0,)

    is_active = Column(Boolean,default=True,)

    reward_level = Column(String,default="Bronze",)

    consecutive_late_payments = Column(Integer,default=0,)

    created_at = Column(DateTime,default=datetime.now,nullable=False,)

    owner_id = Column(Integer,ForeignKey("users.id"),nullable=False,
    )

    loans = relationship(
        "Loan",
        back_populates="client",
        cascade="all, delete-orphan",
    )

    owner = relationship(
        "User",
        back_populates="clients",
    )

class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    amount = Column(Integer, nullable=False,)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_weeks = Column(Integer, default=14)
    status = Column(String, default="active")
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False,)

    payments = relationship("Payment", back_populates="loan", cascade="all, delete-orphan")
    client = relationship("Client",back_populates="loans",)

class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True, index=True)
    payment_number = Column(Integer, nullable=False)
    payment_amount = Column(Integer, nullable=False)
    payment_date = Column(Date, nullable=False)
    paid = Column(Boolean, default=False, nullable=False)
    paid_at = Column(DateTime, nullable=True)

    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False)
    loan = relationship("Loan", back_populates="payments")
