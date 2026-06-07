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

    created_at = Column(
        DateTime,
        default=datetime.now,
        nullable=False
    )

    loans = relationship("Loan", back_populates="owner")

class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    amount = Column(Integer)
    date = Column(Date)
    created_at = Column(DateTime, default=datetime.now)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="loans")
    payments = relationship("Payment", back_populates="loan", cascade="all, delete-orphan")

class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True, index=True)
    payment_number = Column(Integer)
    payment_amount = Column(Integer)
    payment_date = Column(Date)
    paid = Column(Boolean, default=False)

    loan_id = Column(Integer, ForeignKey("loans.id"))
    loan = relationship("Loan", back_populates="payments")
