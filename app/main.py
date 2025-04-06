from fastapi import FastAPI
from app.routes import kyc, score, loan
from app.database import Base, engine
from app.routes import disbursal
from app.routes import bot
from app.routes import admin_ui, user_ui
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request


Base.metadata.create_all(bind=engine)

app = FastAPI(title="GrameenLoan - Unified eKYC + Credit Score + LMS")

app.include_router(kyc.router, prefix="/kyc")
app.include_router(score.router, prefix="/score")
app.include_router(loan.router, prefix="/loan")

app.include_router(disbursal.router, prefix="/disbursal")

app.include_router(bot.router, prefix="/bot")

app.include_router(admin_ui.router)
app.include_router(user_ui.router)


templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def homepage(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})
