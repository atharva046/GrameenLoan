from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import date
from app.database import SessionLocal
from app.models import Borrower, Loan
from app.schemas import LoanApplication, LoanStatusResponse
from app.services.emi_calculator import calculate_emi

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/apply", response_model=LoanStatusResponse)
def apply_loan(data: LoanApplication, db: Session = Depends(get_db)):
    borrower = db.query(Borrower).filter(Borrower.id == data.borrower_id).first()
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")

    credit_score = borrower.credit_score or 0

    if credit_score >= 750:
        max_loan = 300000
    elif credit_score >= 700:
        max_loan = 200000
    elif credit_score >= 650:
        max_loan = 100000
    elif credit_score >= 600:
        max_loan = 50000
    else:
        max_loan = 10000

    if data.loan_amount > max_loan:
        return LoanStatusResponse(status="Rejected", max_loan_eligible=max_loan, emi_amount=0.0)

    emi = calculate_emi(data.loan_amount, 12.0, data.tenure_months)
    loan = Loan(
        borrower_id=data.borrower_id,
        loan_amount=data.loan_amount,
        interest_rate=12.0,
        tenure_months=data.tenure_months,
        emi_amount=emi,
        start_date=date.today(),
        status="Approved"
    )
    db.add(loan)
    db.commit()
    db.refresh(loan)

    return LoanStatusResponse(status="Approved", max_loan_eligible=max_loan, emi_amount=emi)