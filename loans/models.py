from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base

class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    amount = Column(Integer)
    date = Column(Date)

    payments = relationship("Payment", back_populates="loan", cascade="all, delete")

class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True, index=True)
    payment_number = Column(Integer)
    payment_date = Column(Date)
    paid = Column(Boolean)

    loan_id = Column(Integer, ForeignKey("loans.id"))

    loan = relationship("Loan", back_populates="payments")