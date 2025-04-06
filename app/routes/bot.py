from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Borrower, Loan
from googletrans import Translator
from datetime import date
from app.schemas import BotMessageRequest

router = APIRouter()
translator = Translator()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def interpret_intent(text):
    text = text.lower()
    if "emi" in text and ("kab" in text or "due" in text or "date" in text):
        return "next_emi"
    elif "balance" in text or "kitna" in text or "bacha" in text:
        return "loan_balance"
    elif "score" in text or "credit" in text:
        return "credit_score"
    else:
        return "unknown"

@router.post("/message")
def handle_bot_message(request: BotMessageRequest, db: Session = Depends(get_db)):
    borrower_id = request.borrower_id
    message = request.message

    borrower = db.query(Borrower).filter(Borrower.id == borrower_id).first()
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")

    # Translate message to English
    english_message = translator.translate(message, src='auto', dest='en').text
    intent = interpret_intent(english_message)

    reply = "Sorry, I didn’t understand your question."

    if intent == "next_emi":
        loan = db.query(Loan).filter(Loan.borrower_id == borrower_id, Loan.status == "Disbursed").first()
        if loan:
            next_due_date = loan.disbursed_on.replace(day=10) if loan.disbursed_on else "unknown"
            reply = f"Your next EMI of ₹{loan.emi_amount} is due on {next_due_date}."
        else:
            reply = "No active disbursed loan found."

    elif intent == "loan_balance":
        loan = db.query(Loan).filter(Loan.borrower_id == borrower_id, Loan.status == "Disbursed").first()
        if loan:
            total = loan.emi_amount * loan.tenure_months
            reply = f"Your total payable amount is ₹{total} in {loan.tenure_months} EMIs."
        else:
            reply = "You don’t have any disbursed loans."

    elif intent == "credit_score":
        if borrower.credit_score:
            reply = f"Your credit score is {borrower.credit_score}."
        else:
            reply = "Your credit score has not been generated yet."

    # Translate back to vernacular (Hindi)
    final_reply = translator.translate(reply, dest='hi').text
    return {"reply": final_reply}
