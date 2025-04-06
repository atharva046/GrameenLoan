from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Borrower, Loan
from fastapi.responses import RedirectResponse
from typing import Optional
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/user/loan-status/{borrower_id}")
def user_loan_status(
    request: Request,
    borrower_id: int,
    success: Optional[str] = None,
    db: Session = Depends(get_db)
):
    borrower = db.query(Borrower).filter(Borrower.id == borrower_id).first()
    loan = db.query(Loan).filter(Loan.borrower_id == borrower_id).first()

    return templates.TemplateResponse("user/loan_status.html", {
        "request": request,
        "borrower": borrower,
        "loan": loan,
        "success": success
    })



@router.get("/user/kyc")
def show_kyc_upload_form(request: Request):
    return templates.TemplateResponse("user/kyc.html", {"request": request})

from fastapi import Form, UploadFile, File
from app.routes.kyc import complete_kyc  # assuming it's imported properly

@router.post("/user/kyc")
async def submit_kyc_form(
    aadhaar_img: UploadFile = File(...),
    pan_img: UploadFile = File(...),
    photo_img: UploadFile = File(...)
):
    db = SessionLocal()
    try:
        borrower = await complete_kyc(aadhaar_img, pan_img, photo_img, db=db)
        return RedirectResponse(f"/user/loan-status/{borrower.id}?success=kyc", status_code=303)
    finally:
        db.close()
    

@router.get("/user/score")
def show_score_form(request: Request):
    return templates.TemplateResponse("user/score.html", {"request": request})


@router.post("/user/score")
async def submit_score_form(
    request: Request,
    borrower_id: int = Form(...),
    monthly_income: float = Form(...),
    monthly_mobile_spend: float = Form(...),
    monthly_utility_spend: float = Form(...),
    household_size: int = Form(...),
    is_self_employed: str = Form(...)
):
    from app.services.ai_score import predict_credit_score
    from app.schemas import ScoreRequest
    from app.database import SessionLocal
    from app.models import Borrower

    db = SessionLocal()
    borrower = db.query(Borrower).filter(Borrower.id == borrower_id).first()

    if not borrower:
        return templates.TemplateResponse("user/score_result.html", {
            "request": request,
            "error": "Borrower ID not found."
        })

    data = ScoreRequest(
        monthly_income=monthly_income,
        monthly_mobile_spend=monthly_mobile_spend,
        monthly_utility_spend=monthly_utility_spend,
        household_size=household_size,
        is_self_employed=is_self_employed.lower() == "yes"
    )

    result = predict_credit_score(data)
    borrower.credit_score = result.credit_score
    db.commit()
    db.close()

    return templates.TemplateResponse("user/score_result.html", {
        "request": request,
        "result": result
    })


from fastapi.responses import HTMLResponse
from app.schemas import LoanApplication
from app.services.emi_calculator import calculate_emi
from app.models import Borrower, Loan
from datetime import date

@router.get("/user/apply-loan", response_class=HTMLResponse)
def loan_form(request: Request):
    return templates.TemplateResponse("user/apply_loan.html", {"request": request})


@router.post("/user/apply-loan", response_class=HTMLResponse)
async def apply_loan(
    request: Request,
    borrower_id: int = Form(...),
    loan_amount: float = Form(...),
    tenure_months: int = Form(...)
):
    db = SessionLocal()
    borrower = db.query(Borrower).filter(Borrower.id == borrower_id).first()

    if not borrower:
        return RedirectResponse(f"/user/loan-result/{loan.id}?success=applied", status_code=303)

    credit_score = borrower.credit_score or 0

    # Determine max loan and interest rate
    if credit_score >= 750:
        max_loan = 300000
        interest_rate = 9.0
    elif credit_score >= 700:
        max_loan = 200000
        interest_rate = 11.0
    elif credit_score >= 650:
        max_loan = 100000
        interest_rate = 13.0
    elif credit_score >= 600:
        max_loan = 50000
        interest_rate = 16.0
    else:
        max_loan = 10000
        interest_rate = 20.0

    if loan_amount > max_loan:
        return templates.TemplateResponse("user/loan_result.html", {
            "request": request,
            "error": f"Requested loan exceeds your eligibility (₹{max_loan})"
        })

    emi = calculate_emi(loan_amount, interest_rate, tenure_months)

    loan = Loan(
        borrower_id=borrower_id,
        loan_amount=loan_amount,
        interest_rate=interest_rate,
        tenure_months=tenure_months,
        emi_amount=emi,
        start_date=date.today(),
        status="Approved"
    )
    db.add(loan)
    db.commit()
    db.refresh(loan)
    db.close()

    return templates.TemplateResponse("user/loan_result.html", {
        "request": request,
        "loan": loan,
        "borrower": borrower
    })

@router.get("/user/check-loan")
def show_loan_input_form(request: Request):
    return templates.TemplateResponse("user/check_loan.html", {"request": request})

@router.get("/user/chatbot")
def show_chatbot_ui(request: Request):
    return templates.TemplateResponse("user/chatbot.html", {"request": request})

@router.get("/user/edit-kyc/{borrower_id}")
def edit_kyc_form(request: Request, borrower_id: int, db: Session = Depends(get_db)):
    borrower = db.query(Borrower).filter(Borrower.id == borrower_id).first()
    return templates.TemplateResponse("user/edit_kyc.html", {"request": request, "borrower": borrower})

@router.post("/user/edit-kyc/{borrower_id}")
def submit_edit_kyc(request: Request, borrower_id: int, name: str = Form(...), pan_number: str = Form(...), aadhaar_uid: str = Form(...), db: Session = Depends(get_db)):
    borrower = db.query(Borrower).filter(Borrower.id == borrower_id).first()
    if borrower:
        borrower.name = name
        borrower.pan_number = pan_number
        borrower.aadhaar_uid = aadhaar_uid
        db.commit()
    return RedirectResponse(f"/user/loan-status/{borrower_id}", status_code=303)


from fastapi.responses import FileResponse
from xhtml2pdf import pisa
import io
from fastapi import Response

@router.get("/user/download-pdf/{loan_id}")
def download_pdf(loan_id: int, db: Session = Depends(get_db)):
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    borrower = db.query(Borrower).filter(Borrower.id == loan.borrower_id).first()

    html_content = f"""
    <html>
    <body>
        <h1>Loan Application Summary</h1>
        <p><strong>Name:</strong> {borrower.name}</p>
        <p><strong>Borrower ID:</strong> {borrower.id}</p>
        <p><strong>Loan Amount:</strong> ₹{loan.loan_amount}</p>
        <p><strong>Tenure:</strong> {loan.tenure_months} months</p>
        <p><strong>EMI:</strong> ₹{loan.emi_amount}</p>
        <p><strong>Status:</strong> {loan.status}</p>
    </body>
    </html>
    """

    result = io.BytesIO()
    pisa.CreatePDF(html_content, dest=result)
    result.seek(0)
    return Response(content=result.read(), media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=loan_{loan.id}.pdf"
    })

@router.get("/user/loan-result/{loan_id}")
def show_loan_result(loan_id: int, request: Request, success: Optional[str] = None, db: Session = Depends(get_db)):
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    borrower = db.query(Borrower).filter(Borrower.id == loan.borrower_id).first()
    return templates.TemplateResponse("user/loan_result.html", {
        "request": request,
        "loan": loan,
        "borrower": borrower,
        "success": success
    })
