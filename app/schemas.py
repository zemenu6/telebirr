from pydantic import BaseModel, constr, PositiveFloat
from typing import Optional, List
from datetime import datetime
import uuid


class SignupSchema(BaseModel):
    phoneNumber: constr(min_length=10, max_length=15)
    username: constr(min_length=3, max_length=50)
    password: constr(min_length=6)


class LoginSchema(BaseModel):
    phoneNumber: constr(min_length=10, max_length=15)
    password: constr(min_length=6)


class TransferSchema(BaseModel):
    recipientPhone: constr(min_length=10, max_length=15)
    amount: PositiveFloat


class EqubDepositSchema(BaseModel):
    phoneNumber: constr(min_length=10, max_length=15)
    amount: PositiveFloat
    durationMonths: int


class EqubWithdrawSchema(BaseModel):
    phoneNumber: constr(min_length=10, max_length=15)
    equbAccountId: str


class UserResponse(BaseModel):
    success: bool
    message: str
    phoneNumber: str
    username: str
    balance: str


class AuthResponse(BaseModel):
    success: bool
    message: str
    phoneNumber: str
    username: str
    balance: str


class TransactionResponse(BaseModel):
    success: bool
    message: str
    transactionId: str
    newBalance: str


class EqubAccountResponse(BaseModel):
    id: str
    phoneNumber: str
    amount: str
    depositDate: datetime
    maturityDate: datetime
    canWithdraw: bool
    isActive: bool


class EqubDepositResponse(BaseModel):
    success: bool
    message: str
    equbAccount: EqubAccountResponse


class EqubWithdrawResponse(BaseModel):
    success: bool
    message: str
    transactionId: str
    newBalance: str


class BalanceResponse(BaseModel):
    success: bool
    balance: str
    equbAccounts: List[EqubAccountResponse]


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: Optional[str] = None
