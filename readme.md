Of course bro! Here's a clean and professional `README.md` for your **GrameenLoan** project — including all phases, features, setup instructions, and folder structure. Perfect for GitHub, deployment, or presentations.

---

### 📄 `README.md` for GrameenLoan

```markdown
# 🚀 GrameenLoan - AI-Powered Rural Lending Platform

GrameenLoan is an AI-powered, end-to-end microfinance platform designed to help NBFCs streamline rural loan applications. It features digital KYC, AI credit scoring, a mini loan management system, disbursal simulation, vernacular chatbot, and a full admin dashboard — all built with FastAPI, TailwindCSS, and Jinja2.

---

## ✅ Features

### 🧾 Phase 1: e-KYC Upload
- Upload Aadhaar (photo), PAN card, and user selfie
- OCR and image processing to extract name, DOB, PAN, UID
- Data stored securely in SQLite

### 🧠 Phase 2: AI Credit Scoring
- Inputs: income, mobile recharge, utility bills, household size
- Predicts credit score, risk level, and loan eligibility
- Built-in `predict_credit_score()` model with retrainable logic

### 💸 Phase 3: Loan Application
- Apply for a loan using borrower ID and tenure
- EMI auto-calculated based on AI score and interest rate slab
- Loan saved with status = “Approved”

### 🏦 Phase 4: Disbursal Simulator
- IMPS/UPI mock transfer
- Generates random UTR ID
- Updates loan status to “Disbursed”
- Sets `auto_debit_linked = True`

### 🗣️ Phase 5: Vernacular Chatbot
- Users can chat in Hindi/vernacular
- Replies on EMI dates, loan status, credit score, etc.
- Works via `/bot/message` and integrated chat UI

### 🎛️ Admin Panel
- Sidebar with Dashboard, Filters, Search
- Stats: total borrowers, loans, approvals, disbursed
- Search/filter by ID, status, and loan amount
- Built using Tailwind + Jinja2 layout

### 📄 PDF Generation
- After applying, users can download a full loan summary PDF

---

## 🛠 Tech Stack

- **Backend**: FastAPI
- **Frontend**: Jinja2 + Tailwind CSS
- **OCR**: Tesseract via EasyOCR
- **Database**: SQLite with SQLAlchemy
- **PDF**: xhtml2pdf
- **Chatbot**: Custom rule-based + Google Translate (optional)
- **AI Model**: scikit-learn RandomForest (trainable via `train_model.ipynb`)

---

## 📦 Folder Structure



## 🚀 Getting Started

### 1. Clone the Repo
```bash
git clone https://github.com/yourname/grameenloan.git
cd grameenloan
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### 3. Install Requirements
```bash
pip install -r requirements.txt
```

### 4. Run the App
```bash
uvicorn app.main:app --reload
```

### 5. Open in Browser
```
http://127.0.0.1:8000/
```

---

## 📌 Sample Workflows

### KYC → Score → Apply Loan → Status + PDF
1. Go to `/user/kyc` → Upload docs
2. Go to `/user/score` → Get AI score
3. Go to `/user/apply-loan` → Apply
4. Go to `/user/loan-status/{id}` → See loan + download PDF

---

## 👨‍💼 Admin Access

Visit:
```
/admin/dashboard
/admin/search-loans
/admin/dashboard-filters
```

---

## 🤖 Train Your Own Scoring Model

Use `train_model.ipynb` to:
- Load your real data
- Retrain RandomForestClassifier
- Save new `model.pkl` for use in production

---

## 📄 License

MIT License — Free to use with attribution 🙌

---

## 💬 Made with ❤️ to power rural Bharat
```
