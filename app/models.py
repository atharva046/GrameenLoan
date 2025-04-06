from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date,Boolean
from app.database import Base

class Borrower(Base):
    __tablename__ = "borrowers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    dob = Column(String)
    gender = Column(String, nullable=True)
    pan_number = Column(String, unique=True)
    aadhaar_uid = Column(String, unique=True, nullable=True)
    photo_path = Column(String)
    credit_score = Column(Integer, nullable=True)

class Loan(Base):
    __tablename__ = "loans"
    id = Column(Integer, primary_key=True, index=True)
    borrower_id = Column(Integer, ForeignKey("borrowers.id"))
    loan_amount = Column(Float)
    interest_rate = Column(Float)
    tenure_months = Column(Integer)
    emi_amount = Column(Float)
    start_date = Column(Date)
    status = Column(String)
    utr_id = Column(String, nullable=True)  # ✅ New
    disbursed_on = Column(Date, nullable=True)  # ✅ New
    auto_debit_linked = Column(Boolean, default=False)  