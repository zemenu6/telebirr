#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Testing database connection...")
print(f"Database URL: {DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        print(f"✓ Database connected successfully!")
        print(f"PostgreSQL version: {version}")
        
        # Test if users table exists
        result = connection.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users');"))
        table_exists = result.fetchone()[0]
        print(f"Users table exists: {'✓ Yes' if table_exists else '✗ No'}")
        
except Exception as e:
    print(f"✗ Database connection failed: {e}")