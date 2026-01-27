from pydantic import BaseModel, constr, PositiveFloat, validator
from typing import Optional, List
from datetime import datetime
import uuid
import re


# Request schemas
class SignupRequest(BaseModel):
    phoneNumber: constr(min_length=10, max_length=10)
    username: constr(min_length=2, max_length=50)
    password: constr(min_length=6, max_length=6)
    
    @validator('phoneNumber')
    def validate_phone(cls, v):
        if not re.match(r'^09[0-9]{8}$', v):
            raise ValueError('Phone number must be in format 09XXXXXXXX')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if not re.match(r'^[a-zA-Z0-9]{6}$', v):
            raise ValueError('Password must be exactly 6 alphanumeric characters')
        return v


class LoginRequest(BaseModel):
    phoneNumber: constr(min_length=10, max_length=10)
    password: constr(min_length=6, max_length=6)
    
    @validator('phoneNumber')
    def validate_phone(cls, v):
        if not re.match(r'^09[0-9]{8}$', v):
            raise ValueError('Phone number must be in format 09XXXXXXXX')
        return v


class SendMoneyRequest(BaseModel):
    recipientPhone: constr(min_length=10, max_length=10)
    amount: PositiveFloat
    
    @validator('recipientPhone')
    def validate_phone(cls, v):
        if not re.match(r'^09[0-9]{8}$', v):
            raise ValueError('Phone number must be in format 09XXXXXXXX')
        return v
    
    @validator('amount')
    def validate_amount(cls, v):
        if v > 100000:
            raise ValueError('Maximum transfer amount is 100,000 Birr')
        if v < 1:
            raise ValueError('Minimum transfer amount is 1 Birr')
        return v


class EqubDepositRequest(BaseModel):
    phoneNumber: constr(min_length=10, max_length=10)
    amount: PositiveFloat
    durationMonths: int = 1
    
    @validator('phoneNumber')
    def validate_phone(cls, v):
        if not re.match(r'^09[0-9]{8}$', v):
            raise ValueError('Phone number must be in format 09XXXXXXXX')
        return v
    
    @validator('amount')
    def validate_amount(cls, v):
        if v < 500:
            raise ValueError('Minimum equb deposit is 500 Birr')
        if v > 50000:
            raise ValueError('Maximum equb deposit is 50,000 Birr')
        return v
    
    @validator('durationMonths')
    def validate_duration(cls, v):
        if v != 1:
            raise ValueError('Equb duration must be exactly 1 month')
        return v


class EqubWithdrawRequest(BaseModel):
    phoneNumber: constr(min_length=10, max_length=10)
    equbAccountId: str
    
    @validator('phoneNumber')
    def validate_phone(cls, v):
        if not re.match(r'^09[0-9]{8}$', v):
            raise ValueError('Phone number must be in format 09XXXXXXXX')
        return v
    
    @validator('equbAccountId')
    def validate_uuid(cls, v):
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError('Invalid equb account ID format')
        return v


class AuthResponse(BaseModel):
    success: bool
    message: str
    phoneNumber: Optional[str] = None
    username: Optional[str] = None
    balance: Optional[str] = None


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
