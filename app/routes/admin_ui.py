from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Borrower, Loan
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/admin/dashboard")
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    total_borrowers = db.query(Borrower).count()
    total_loans = db.query(Loan).count()
    disbursed = db.query(Loan).filter(Loan.status == "Disbursed").count()
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "total_borrowers": total_borrowers,
        "total_loans": total_loans,
        "disbursed": disbursed
    })

@router.get("/admin/loans")
def view_loans(request: Request, db: Session = Depends(get_db)):
    loans = db.query(Loan).all()
    return templates.TemplateResponse("admin/loans.html", {
        "request": request,
        "loans": loans
    })


@router.get("/admin/search-loans")
def search_loans(
    request: Request,
    borrower_id: Optional[str] = None,
    status: Optional[str] = None,
    min_amount: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Loan)

    # Clean and convert values
    if borrower_id and borrower_id.isdigit():
        query = query.filter(Loan.borrower_id == int(borrower_id))

    if status:
        query = query.filter(Loan.status.ilike(f"%{status}%"))

    if min_amount and min_amount.isdigit():
        query = query.filter(Loan.loan_amount >= int(min_amount))

    loans = query.all()
    return templates.TemplateResponse("admin/search_loans.html", {"request": request, "loans": loans})

@router.get("/admin/dashboard-filters")
def filtered_dashboard(request: Request, status: str = None, min_amount: int = None, db: Session = Depends(get_db)):
    total_borrowers = db.query(Borrower).count()
    query = db.query(Loan)
    if status:
        query = query.filter(Loan.status == status)
    if min_amount:
        query = query.filter(Loan.loan_amount >= min_amount)
    filtered_loans = query.count()
    return templates.TemplateResponse("admin/dashboard_filters.html", {
        "request": request,
        "total_borrowers": total_borrowers,
        "filtered_loans": filtered_loans,
        "selected_status": status
    })
