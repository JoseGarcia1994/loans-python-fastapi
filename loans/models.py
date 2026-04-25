from sqlalchemy import Column, Integer, String, Date

from database import Base

class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    amount = Column(Integer)
    date = Column(Date)

