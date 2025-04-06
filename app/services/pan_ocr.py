import easyocr
import re
import torch

reader = easyocr.Reader(['en'], gpu=torch.cuda.is_available())

def extract_pan_data(image_path: str):
    result = reader.readtext(image_path, detail=0)
    pan_data = {"name": "", "dob": "", "pan_number": ""}
    for line in result:
        if "/" in line and len(line) >= 10:
            pan_data["dob"] = line
        elif len(line) == 10 and line.isalnum():
            pan_data["pan_number"] = line.upper()
        elif pan_data["name"] == "":
            pan_data["name"] = line.title()
    return pan_data



def extract_aadhaar_data(image_path: str):
    result = reader.readtext(image_path, detail=0)
    aadhaar_data = {
        "name": "",
        "dob": "",
        "aadhaar_uid": "",
        "gender": ""
    }

    for line in result:
        line = line.strip()
        line_lower = line.lower()

        # Aadhaar UID
        if re.search(r"\b\d{4}\s\d{4}\s\d{4}\b", line):
            aadhaar_data["aadhaar_uid"] = line.replace(" ", "")

        # Gender
        elif "male" in line_lower:
            aadhaar_data["gender"] = "Male"
        elif "female" in line_lower:
            aadhaar_data["gender"] = "Female"

        # DOB (matches dd/mm/yyyy or dd-mm-yyyy)
        elif re.search(r"\b\d{2}[-/]\d{2}[-/]\d{4}\b", line):
            aadhaar_data["dob"] = line

        # Name - filter out known noise terms
        elif aadhaar_data["name"] == "" and line.replace(" ", "").isalpha() and not any(
            word in line_lower for word in ["government", "india", "authority", "year", "male", "female", "dob", "uid"]
        ):
            aadhaar_data["name"] = line.title()

    print("[OCR RAW TEXT]", result)
    print("[PARSED AADHAAR DATA]", aadhaar_data)
    return aadhaar_data
