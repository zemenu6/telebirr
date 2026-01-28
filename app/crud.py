from sqlalchemy.orm import Session
from sqlalchemy import select
from passlib.context import CryptContext
from . import models
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    # Ensure password is within bcrypt 72-byte limit
    if len(password.encode('utf-8')) > 72:
        password = password[:72]
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_phone(db: Session, phone_number: str):
    return db.query(models.User).filter(models.User.phone_number == phone_number).first()

def create_user(db: Session, phone_number: str, username: str, password: str, initial_balance: float = 0.0):
    try:
        hashed = get_password_hash(password)
        user = models.User(
            phone_number=phone_number, 
            username=username, 
            password_hash=hashed, 
            balance=Decimal(str(initial_balance))
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        raise e

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
        amount=Decimal(str(amount)), 
        transaction_type=models.TransactionType(transaction_type),
        status=models.TransactionStatus.COMPLETED,
        created_at=datetime.utcnow()
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


def transfer_money(db: Session, from_phone: str, to_phone: str, amount: float):
    try:
        # Start explicit transaction
        sender = get_user_by_phone(db, from_phone)
        receiver = get_user_by_phone(db, to_phone)
        
        if sender is None:
            return False, "Sender not found"
        if receiver is None:
            return False, "Recipient not found"
        if sender.balance < Decimal(str(amount)):
            return False, "Insufficient balance"

        # Update balances
        sender.balance -= Decimal(str(amount))
        receiver.balance += Decimal(str(amount))
        
        # Save changes
        db.add(sender)
        db.add(receiver)
        db.flush()  # Flush to get updated balances
        
        # Create transaction record
        tx = models.Transaction(
            from_phone=from_phone, 
            to_phone=to_phone, 
            amount=Decimal(str(amount)), 
            transaction_type=models.TransactionType.TRANSFER,
            status=models.TransactionStatus.COMPLETED,
            created_at=datetime.utcnow()
        )
        db.add(tx)
        
        # Commit all changes together
        db.commit()
        db.refresh(tx)
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
    
    if user.balance < Decimal(str(amount)):
        return False, "Insufficient balance"
    
    # For testing: make equb mature immediately (remove this in production)
    maturity_date = datetime.utcnow() + timedelta(seconds=30)  # 30 seconds for testing
    
    try:
        user.balance -= Decimal(str(amount))
        db.add(user)
        
        equb_account = models.EqubAccount(
            phone_number=phone_number,
            amount=Decimal(str(amount)),
            deposit_date=datetime.utcnow(),
            maturity_date=maturity_date,
            can_withdraw=False,  # Will be set to True after 30 seconds
            is_active=True
        )
        db.add(equb_account)
        
        tx = models.Transaction(
            from_phone=phone_number, 
            to_phone=phone_number, 
            amount=Decimal(str(amount)), 
            transaction_type=models.TransactionType.EQUB_DEPOSIT,
            status=models.TransactionStatus.COMPLETED,
            created_at=datetime.utcnow()
        )
        db.add(tx)
        
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
        
        tx = create_transaction(db, phone_number, phone_number, float(equb_account.amount), 'EQUB_WITHDRAWAL')
        
        db.commit()
        return True, tx
    except Exception as e:
        db.rollback()
        return False, str(e)


def get_user_transactions(db: Session, phone_number: str):
    return db.query(models.Transaction).filter(
        (models.Transaction.from_phone == phone_number) | 
        (models.Transaction.to_phone == phone_number)
    ).order_by(models.Transaction.created_at.desc()).limit(50).all()


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
