import joblib
import os
from app.schemas import ScoreRequest, ScoreResponse

model_path = os.path.join("ai_model", "credit_model.pkl")
try:
    model = joblib.load(model_path)
except Exception as e:
    print(f"[ERROR] Failed to load model: {e}")
    model = None

def predict_credit_score(data: ScoreRequest) -> ScoreResponse:
    input_array = [[
        data.monthly_income,
        data.monthly_mobile_spend,
        data.monthly_utility_spend,
        data.household_size,
        1 if data.is_self_employed else 0
    ]]

    predicted_score = int(model.predict(input_array)[0])

    if predicted_score >= 750:
        risk = "Very Low"
        max_loan = 300000
    elif predicted_score >= 700:
        risk = "Low"
        max_loan = 200000
    elif predicted_score >= 650:
        risk = "Moderate"
        max_loan = 100000
    elif predicted_score >= 600:
        risk = "High"
        max_loan = 50000
    else:
        risk = "Very High"
        max_loan = 10000

    return ScoreResponse(
        credit_score=predicted_score,
        risk_level=risk,
        max_loan_eligible=max_loan
    )