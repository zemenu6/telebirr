import os
from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from . import models, crud, schemas, auth, exceptions
from typing import Dict
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:1dBufXeykxdVBsrJ@mctmbhyqosnmbqorlhna.db.eu-central-1.nhost.run:5432/mctmbhyqosnmbqorlhna")
SECRET_KEY = os.getenv("SECRET_KEY", "changeme")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(title="TeleBirr API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(HTTPException, exceptions.http_exception_handler)
app.add_exception_handler(RequestValidationError, exceptions.validation_exception_handler)
app.add_exception_handler(Exception, exceptions.general_exception_handler)


@app.on_event("startup")
def on_startup():
    models.Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "TeleBirr API is running"}


@app.post("/auth/signup", response_model=schemas.UserResponse)
def signup(payload: schemas.SignupSchema, db=Depends(get_db)):
    existing = crud.get_user_by_phone(db, payload.phoneNumber)
    if existing:
        raise exceptions.TeleBirrException("Phone number already registered", "PHONE_EXISTS")
    
    user = crud.create_user(db, payload.phoneNumber, payload.username, payload.password, initial_balance=0.0)
    return {
        "success": True,
        "message": "Account created successfully",
        "phoneNumber": user.phone_number,
        "username": user.username,
        "balance": f"{user.balance:.2f}"
    }


@app.post("/auth/login", response_model=schemas.AuthResponse)
def login(payload: schemas.LoginSchema, db=Depends(get_db)):
    user = crud.authenticate_user(db, payload.phoneNumber, payload.password)
    if not user:
        raise exceptions.TeleBirrException("Invalid credentials", "INVALID_CREDENTIALS")
    
    return {
        "success": True,
        "message": "Login successful",
        "phoneNumber": user.phone_number,
        "username": user.username,
        "balance": f"{user.balance:.2f}"
    }


@app.post("/transactions/send-money", response_model=schemas.TransactionResponse)
def send_money(payload: schemas.TransferSchema, db=Depends(get_db), token_user=Depends(auth.verify_token)):
    if token_user.phone_number == payload.recipientPhone:
        raise exceptions.TeleBirrException("Cannot send money to yourself", "SELF_TRANSFER")
    
    ok, result = crud.transfer_money(db, token_user.phone_number, payload.recipientPhone, payload.amount)
    if not ok:
        if "Insufficient balance" in result:
            raise exceptions.InsufficientFundsException()
        elif "not found" in result:
            raise exceptions.UserNotFoundException()
        else:
            raise exceptions.TeleBirrException(result, "TRANSFER_FAILED")
    
    return {
        "success": True,
        "message": "Money sent successfully",
        "transactionId": str(result.id),
        "newBalance": f"{token_user.balance:.2f}"
    }


@app.post("/equb/deposit", response_model=schemas.EqubDepositResponse)
def equb_deposit(payload: schemas.EqubDepositSchema, db=Depends(get_db), token_user=Depends(auth.verify_token)):
    if token_user.phone_number != payload.phoneNumber:
        raise exceptions.TeleBirrException("Token user does not match phone number", "TOKEN_MISMATCH")
    
    ok, result = crud.create_equb_account(db, payload.phoneNumber, payload.amount, payload.durationMonths)
    if not ok:
        if "Minimum deposit" in result:
            raise exceptions.MinimumDepositException()
        elif "Insufficient balance" in result:
            raise exceptions.InsufficientFundsException()
        elif "not found" in result:
            raise exceptions.UserNotFoundException()
        else:
            raise exceptions.TeleBirrException(result, "EQUB_DEPOSIT_FAILED")
    
    return {
        "success": True,
        "message": "Equb deposit successful",
        "equbAccount": {
            "id": str(result.id),
            "phoneNumber": result.phone_number,
            "amount": f"{result.amount:.2f}",
            "depositDate": result.deposit_date,
            "maturityDate": result.maturity_date,
            "canWithdraw": result.can_withdraw,
            "isActive": result.is_active
        }
    }


@app.post("/equb/withdraw", response_model=schemas.EqubWithdrawResponse)
def equb_withdraw(payload: schemas.EqubWithdrawSchema, db=Depends(get_db), token_user=Depends(auth.verify_token)):
    if token_user.phone_number != payload.phoneNumber:
        raise exceptions.TeleBirrException("Token user does not match phone number", "TOKEN_MISMATCH")
    
    ok, result = crud.withdraw_equb(db, payload.phoneNumber, payload.equbAccountId)
    if not ok:
        if "not found" in result:
            raise exceptions.EqubNotFoundException()
        elif "not mature" in result:
            raise exceptions.EqubNotMatureException()
        elif "Invalid" in result:
            raise exceptions.TeleBirrException(result, "INVALID_EQUB_ID")
        else:
            raise exceptions.TeleBirrException(result, "EQUB_WITHDRAW_FAILED")
    
    return {
        "success": True,
        "message": "Equb withdrawal successful",
        "transactionId": str(result.id),
        "newBalance": f"{token_user.balance:.2f}"
    }


@app.get("/user/balance", response_model=schemas.BalanceResponse)
def get_balance(phoneNumber: str = Query(...), db=Depends(get_db), token_user=Depends(auth.verify_token)):
    if token_user.phone_number != phoneNumber:
        raise exceptions.TeleBirrException("Token user does not match phone number", "TOKEN_MISMATCH")
    
    user = crud.get_user_by_phone(db, phoneNumber)
    if not user:
        raise exceptions.UserNotFoundException()
    
    equb_accounts = crud.get_equb_accounts(db, phoneNumber)
    
    equb_account_responses = []
    for account in equb_accounts:
        equb_account_responses.append({
            "id": str(account.id),
            "phoneNumber": account.phone_number,
            "amount": f"{account.amount:.2f}",
            "depositDate": account.deposit_date,
            "maturityDate": account.maturity_date,
            "canWithdraw": account.can_withdraw,
            "isActive": account.is_active
        })
    
    return {
        "success": True,
        "balance": f"{user.balance:.2f}",
        "equbAccounts": equb_account_responses
    }
