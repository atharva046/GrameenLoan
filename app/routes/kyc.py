from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
import shutil, os
from app.database import SessionLocal
from app.models import Borrower
from app.schemas import BorrowerResponse
from app.services.pan_ocr import extract_pan_data, extract_aadhaar_data

router = APIRouter()
UPLOAD_DIR = "app/uploads"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/complete", response_model=BorrowerResponse, operation_id="kyc_complete_upload")
async def complete_kyc(
    pan_file: UploadFile = File(...),
    aadhaar_file: UploadFile = File(...),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    pan_path = os.path.join(UPLOAD_DIR, "pan", pan_file.filename)
    with open(pan_path, "wb") as f:
        shutil.copyfileobj(pan_file.file, f)
    pan_data = extract_pan_data(pan_path)

    aadhaar_path = os.path.join(UPLOAD_DIR, "aadhaar", aadhaar_file.filename)
    with open(aadhaar_path, "wb") as f:
        shutil.copyfileobj(aadhaar_file.file, f)
    aadhaar_data = extract_aadhaar_data(aadhaar_path)

    photo_path = os.path.join(UPLOAD_DIR, "photo", photo.filename)
    with open(photo_path, "wb") as f:
        shutil.copyfileobj(photo.file, f)

    borrower = Borrower(
        name=aadhaar_data["name"] if aadhaar_data["name"] else pan_data["name"],
    dob=aadhaar_data["dob"] if aadhaar_data["dob"] else pan_data["dob"],
    pan_number=pan_data["pan_number"],
    aadhaar_uid=aadhaar_data["aadhaar_uid"],
    gender=aadhaar_data["gender"],
    photo_path=photo_path
    )
    db.add(borrower)
    db.commit()
    db.refresh(borrower)
    return borrower