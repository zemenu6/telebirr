from datetime import datetime
from sqlalchemy import Column, String, DECIMAL, DateTime, ForeignKey, Boolean, UUID, Enum
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
import uuid
import enum

Base = declarative_base()

class TransactionType(enum.Enum):
    TRANSFER = "TRANSFER"
    EQUB_DEPOSIT = "EQUB_DEPOSIT"
    EQUB_WITHDRAWAL = "EQUB_WITHDRAWAL"

class TransactionStatus(enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class User(Base):
    __tablename__ = "users"
    phone_number = Column(String(15), primary_key=True)
    username = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    balance = Column(DECIMAL(15,2), default=0.00)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class EqubAccount(Base):
    __tablename__ = "equb_accounts"
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String(15), ForeignKey("users.phone_number", ondelete="CASCADE"))
    amount = Column(DECIMAL(15,2), nullable=False)
    deposit_date = Column(DateTime, default=datetime.utcnow)
    maturity_date = Column(DateTime, nullable=False)
    can_withdraw = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", foreign_keys=[phone_number])

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    from_phone = Column(String(15), ForeignKey("users.phone_number"))
    to_phone = Column(String(15), ForeignKey("users.phone_number"))
    amount = Column(DECIMAL(15,2), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    description = Column(String)
    reference_id = Column(String(50))
    equb_account_id = Column(PostgresUUID(as_uuid=True), ForeignKey("equb_accounts.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    from_user = relationship("User", foreign_keys=[from_phone])
    to_user = relationship("User", foreign_keys=[to_phone])
