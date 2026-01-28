import os
from fastapi import FastAPI, Depends, HTTPException, status, Query, Request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from . import models, crud, schemas, auth, exceptions, rate_limiter
from typing import Dict
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

load_dotenv()

# Use environment variables with secure defaults
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secure-secret-key-change-in-production")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

if SECRET_KEY == "your-secure-secret-key-change-in-production":
    print("WARNING: Using default SECRET_KEY. Change in production!")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user():
    def dependency(phone_number: str = Depends(auth.verify_token_only), db: Session = Depends(get_db)):
        # Sync user from Nhost to local database if needed
        user = auth.sync_user_with_nhost(phone_number, db)
        return user
    return dependency


app = FastAPI(title="TeleBirr API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://federal-blisse-telebirr-56e12994.koyeb.app", "https://mctmbhyqosnmbqorlhna.functions.nhost.run"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

# Exception handlers
app.add_exception_handler(HTTPException, exceptions.http_exception_handler)
app.add_exception_handler(RequestValidationError, exceptions.validation_exception_handler)
app.add_exception_handler(Exception, exceptions.general_exception_handler)


@app.on_event("startup")
def on_startup():
    # Skip automatic table creation for production
    # Tables should be created manually using schema.sql
    pass


@app.get("/")
def root():
    return {"message": "TeleBirr API is running", "status": "healthy"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "not_connected"}


# Authentication endpoints
@app.post("/auth/signup", response_model=schemas.AuthResponse)
def signup(payload: schemas.SignupRequest, db=Depends(get_db)):
    # Check if user already exists
    existing_user = crud.get_user_by_phone(db, payload.phoneNumber)
    if existing_user:
        raise HTTPException(status_code=409, detail="Phone number already registered")
    
    # Create user with initial balance of 1000 Birr for testing
    user = crud.create_user(db, payload.phoneNumber, payload.username, payload.password, 1000.0)
    if not user:
        raise HTTPException(status_code=500, detail="Failed to create user")
    
    return {
        "success": True,
        "message": "Account created successfully",
        "phoneNumber": user.phone_number,
        "username": user.username,
        "balance": f"{user.balance:.2f}"
    }

@app.post("/auth/login", response_model=schemas.AuthResponse)
def login(payload: schemas.LoginRequest, db=Depends(get_db)):
    # Verify user credentials
    user = crud.authenticate_user(db, payload.phoneNumber, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid phone number or password")
    
    return {
        "success": True,
        "message": "Login successful",
        "phoneNumber": user.phone_number,
        "username": user.username,
        "balance": f"{user.balance:.2f}"
    }


@app.post("/transactions/send-money", response_model=schemas.TransactionResponse)
def send_money(payload: schemas.SendMoneyRequest, db=Depends(get_db)):
    # TEMPORARY: Get sender phone from first available user
    # In production, this should come from authentication token
    sender = db.query(models.User).filter(models.User.balance > 0).first()
    if not sender:
        # Create a test user if none exists
        sender = crud.create_user(db, "0900000000", "Test Sender", "test12", 5000.0)
    
    if sender.phone_number == payload.recipientPhone:
        raise HTTPException(status_code=400, detail="Cannot send money to yourself")
    
    ok, result = crud.transfer_money(db, sender.phone_number, payload.recipientPhone, float(payload.amount))
    if not ok:
        if "Insufficient balance" in result:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        elif "not found" in result:
            raise HTTPException(status_code=404, detail="Recipient not found")
        else:
            raise HTTPException(status_code=500, detail=result)
    
    # Refresh sender to get updated balance
    db.refresh(sender)
    return {
        "success": True,
        "message": "Money sent successfully",
        "transactionId": str(result.id),
        "newBalance": f"{sender.balance:.2f}"
    }


@app.post("/equb/deposit", response_model=schemas.EqubDepositResponse)
def equb_deposit(payload: schemas.EqubDepositRequest, db=Depends(get_db)):
    ok, result = crud.create_equb_account(db, payload.phoneNumber, float(payload.amount), payload.durationMonths)
    if not ok:
        if "Minimum deposit" in result:
            raise HTTPException(status_code=400, detail="Minimum deposit is 500 Birr")
        elif "Insufficient balance" in result:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        elif "not found" in result:
            raise HTTPException(status_code=404, detail="User not found")
        else:
            raise HTTPException(status_code=500, detail=result)
    
    return {
        "success": True,
        "message": "Equb deposit successful",
        "equbAccount": {
            "id": str(result.id),
            "phoneNumber": result.phone_number,
            "amount": f"{result.amount:.2f}",
            "depositDate": result.deposit_date.isoformat(),
            "maturityDate": result.maturity_date.isoformat(),
            "canWithdraw": result.can_withdraw,
            "isActive": result.is_active
        }
    }


@app.post("/equb/withdraw", response_model=schemas.EqubWithdrawResponse)
def equb_withdraw(payload: schemas.EqubWithdrawRequest, db=Depends(get_db)):
    ok, result = crud.withdraw_equb(db, payload.phoneNumber, payload.equbAccountId)
    if not ok:
        if "not found" in result:
            raise HTTPException(status_code=404, detail="Equb account not found")
        elif "not mature" in result:
            raise HTTPException(status_code=400, detail="Equb not mature for withdrawal")
        elif "Invalid" in result:
            raise HTTPException(status_code=400, detail="Invalid equb account ID")
        else:
            raise HTTPException(status_code=500, detail=result)
    
    user = crud.get_user_by_phone(db, payload.phoneNumber)
    return {
        "success": True,
        "message": "Equb withdrawal successful",
        "transactionId": str(result.id),
        "newBalance": f"{user.balance:.2f}"
    }


@app.get("/user/balance", response_model=schemas.BalanceResponse)
def get_balance(phoneNumber: str = Query(...), db=Depends(get_db)):
    user = crud.get_user_by_phone(db, phoneNumber)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    equb_accounts = crud.get_equb_accounts(db, phoneNumber)
    
    equb_account_responses = []
    for account in equb_accounts:
        equb_account_responses.append({
            "id": str(account.id),
            "phoneNumber": account.phone_number,
            "amount": f"{account.amount:.2f}",
            "depositDate": account.deposit_date.isoformat(),
            "maturityDate": account.maturity_date.isoformat(),
            "canWithdraw": account.can_withdraw,
            "isActive": account.is_active
        })
    
    return {
        "success": True,
        "balance": f"{user.balance:.2f}",
        "equbAccounts": equb_account_responses
    }
