from sqlalchemy.orm import Session
from sqlalchemy import select
from passlib.context import CryptContext
from . import models
from datetime import datetime, timedelta
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_user_by_phone(db: Session, phone_number: str):
    return db.query(models.User).filter(models.User.phone_number == phone_number).first()


def create_user(db: Session, phone_number: str, username: str, password: str, initial_balance: float = 0.0):
    hashed = get_password_hash(password)
    user = models.User(phone_number=phone_number, username=username, password_hash=hashed, balance=initial_balance)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, phone_number: str, password: str):
    user = get_user_by_phone(db, phone_number)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def create_transaction(db: Session, from_phone: str, to_phone: str, amount: float, transaction_type: str):
    tx = models.Transaction(
        from_phone=from_phone, 
        to_phone=to_phone, 
        amount=amount, 
        transaction_type=transaction_type,
        status='COMPLETED',
        created_at=datetime.utcnow()
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


def transfer_money(db: Session, from_phone: str, to_phone: str, amount: float):
    sender = get_user_by_phone(db, from_phone)
    receiver = get_user_by_phone(db, to_phone)
    if sender is None:
        return False, "Sender not found"
    if receiver is None:
        return False, "Recipient not found"
    if sender.balance < amount:
        return False, "Insufficient balance"

    try:
        sender.balance -= amount
        receiver.balance += amount
        db.add(sender)
        db.add(receiver)
        tx = create_transaction(db, from_phone, to_phone, amount, 'TRANSFER')
        return True, tx
    except Exception as e:
        db.rollback()
        return False, str(e)


def create_equb_account(db: Session, phone_number: str, amount: float, duration_months: int):
    if amount < 500:
        return False, "Minimum deposit amount is 500 Birr"
    
    user = get_user_by_phone(db, phone_number)
    if not user:
        return False, "User not found"
    
    if user.balance < amount:
        return False, "Insufficient balance"
    
    maturity_date = datetime.utcnow() + timedelta(days=30 * duration_months)
    
    try:
        user.balance -= amount
        db.add(user)
        
        equb_account = models.EqubAccount(
            phone_number=phone_number,
            amount=amount,
            deposit_date=datetime.utcnow(),
            maturity_date=maturity_date,
            can_withdraw=False,
            is_active=True
        )
        db.add(equb_account)
        
        tx = create_transaction(db, phone_number, phone_number, amount, 'EQUB_DEPOSIT')
        
        db.commit()
        db.refresh(equb_account)
        return True, equb_account
    except Exception as e:
        db.rollback()
        return False, str(e)


def get_equb_accounts(db: Session, phone_number: str):
    return db.query(models.EqubAccount).filter(
        models.EqubAccount.phone_number == phone_number,
        models.EqubAccount.is_active == True
    ).all()


def withdraw_equb(db: Session, phone_number: str, equb_account_id: str):
    user = get_user_by_phone(db, phone_number)
    if not user:
        return False, "User not found"
    
    try:
        equb_uuid = uuid.UUID(equb_account_id)
    except ValueError:
        return False, "Invalid equb account ID"
    
    equb_account = db.query(models.EqubAccount).filter(
        models.EqubAccount.id == equb_uuid,
        models.EqubAccount.phone_number == phone_number,
        models.EqubAccount.is_active == True
    ).first()
    
    if not equb_account:
        return False, "Equb account not found"
    
    if not equb_account.can_withdraw and equb_account.maturity_date > datetime.utcnow():
        return False, "Equb account not mature for withdrawal"
    
    try:
        equb_account.can_withdraw = True
        equb_account.is_active = False
        user.balance += equb_account.amount
        
        db.add(user)
        db.add(equb_account)
        
        tx = create_transaction(db, phone_number, phone_number, equb_account.amount, 'EQUB_WITHDRAWAL')
        
        db.commit()
        return True, tx
    except Exception as e:
        db.rollback()
        return False, str(e)


def update_equb_maturity(db: Session):
    equb_accounts = db.query(models.EqubAccount).filter(
        models.EqubAccount.maturity_date <= datetime.utcnow(),
        models.EqubAccount.can_withdraw == False,
        models.EqubAccount.is_active == True
    ).all()
    
    for account in equb_accounts:
        account.can_withdraw = True
        db.add(account)
    
    db.commit()
    return len(equb_accounts)
