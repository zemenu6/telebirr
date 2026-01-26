from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Boolean, UUID
from sqlalchemy.orm import relationship, declarative_base
import uuid

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    phone_number = Column(String(15), primary_key=True)
    username = Column(String(50), nullable=False)
    password_hash = Column(String(255), nullable=False)
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class EqubAccount(Base):
    __tablename__ = "equb_accounts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String(15), ForeignKey("users.phone_number"))
    amount = Column(Float, nullable=False)
    deposit_date = Column(DateTime, default=datetime.utcnow)
    maturity_date = Column(DateTime, nullable=False)
    can_withdraw = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    user = relationship("User", foreign_keys=[phone_number])


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    from_phone = Column(String(15), ForeignKey("users.phone_number"))
    to_phone = Column(String(15), ForeignKey("users.phone_number"))
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(20), nullable=False)  # 'TRANSFER', 'EQUB_DEPOSIT', 'EQUB_WITHDRAWAL'
    status = Column(String(20), default='PENDING')  # 'PENDING', 'COMPLETED', 'FAILED'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    from_user = relationship("User", foreign_keys=[from_phone])
    to_user = relationship("User", foreign_keys=[to_phone])
