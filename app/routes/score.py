from fastapi import APIRouter, Depends, HTTPException,Query
from sqlalchemy.orm import Session
from app.schemas import ScoreRequest, ScoreResponse
from app.services.ai_score import predict_credit_score
from app.models import Borrower
from app.database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/evaluate", response_model=ScoreResponse, operation_id="evaluate_credit_score")
def evaluate_credit_score(
    data: ScoreRequest,
    borrower_id: int = Query(..., description="ID of the borrower"),
    db: Session = Depends(get_db)
):
    borrower = db.query(Borrower).filter(Borrower.id == borrower_id).first()
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")

    result = predict_credit_score(data)
    borrower.credit_score = result.credit_score
    db.commit()
    return result