from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import date
import random
import string
from app.database import SessionLocal
from app.models import Loan
from app.schemas import DisbursalRequest, DisbursalResponse

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_mock_utr():
    return "IMPS" + ''.join(random.choices(string.digits, k=10))

@router.post("/initiate", response_model=DisbursalResponse)
def initiate_disbursal(data: DisbursalRequest, db: Session = Depends(get_db)):
    loan = db.query(Loan).filter(Loan.id == data.loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    if loan.status != "Approved":
        raise HTTPException(status_code=400, detail="Loan is not in 'Approved' state")

    loan.utr_id = generate_mock_utr()
    loan.disbursed_on = date.today()
    loan.auto_debit_linked = True
    loan.status = "Disbursed"

    db.commit()
    db.refresh(loan)

    return DisbursalResponse(
        status=loan.status,
        utr_id=loan.utr_id,
        auto_debit_linked=loan.auto_debit_linked
    )
