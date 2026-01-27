#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
sys.path.append('/home/daggy/Pictures/telebir/bellebirr')

from app import models, crud

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

print("Testing direct user creation...")

try:
    db = SessionLocal()
    
    # Test user creation
    user = crud.create_user(db, "0912345678", "Test", "test12")
    print(f"✓ User created: {user.phone_number}, {user.username}, Balance: {user.balance}")
    
    db.close()
    
except Exception as e:
    print(f"✗ User creation failed: {e}")
    import traceback
    traceback.print_exc()