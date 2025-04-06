from pydantic import BaseModel
from typing import Optional

class BorrowerCreate(BaseModel):
    name: str
    dob: str
    pan_number: str
    aadhaar_uid: Optional[str]
    gender: Optional[str]
    photo_path: Optional[str]
    credit_score: Optional[int] = None

class BorrowerResponse(BorrowerCreate):
    id: int
    class Config:
        from_attributes = True

class ScoreRequest(BaseModel):
    monthly_income: float
    monthly_mobile_spend: float
    monthly_utility_spend: float
    household_size: int
    is_self_employed: bool

class ScoreResponse(BaseModel):
    credit_score: int
    risk_level: str
    max_loan_eligible: int

class LoanApplication(BaseModel):
    borrower_id: int
    loan_amount: float
    tenure_months: int

class LoanStatusResponse(BaseModel):
    status: str
    max_loan_eligible: int
    emi_amount: float

class DisbursalRequest(BaseModel):
    loan_id: int

class DisbursalResponse(BaseModel):
    status: str
    utr_id: str
    auto_debit_linked: bool

class BotMessageRequest(BaseModel):
    borrower_id: int
    message: str
