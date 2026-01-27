#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# Basic tables only
basic_schema = """
-- Users table
CREATE TABLE IF NOT EXISTS users (
    phone_number VARCHAR(15) PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    balance DECIMAL(15,2) DEFAULT 0.00 CHECK (balance >= 0),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Equb accounts table
CREATE TABLE IF NOT EXISTS equb_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number VARCHAR(15) NOT NULL REFERENCES users(phone_number) ON DELETE CASCADE,
    amount DECIMAL(15,2) NOT NULL CHECK (amount >= 500.00),
    deposit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    maturity_date TIMESTAMP NOT NULL,
    can_withdraw BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transaction types
DO $$ BEGIN
    CREATE TYPE transaction_type AS ENUM ('TRANSFER', 'EQUB_DEPOSIT', 'EQUB_WITHDRAWAL');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE transaction_status AS ENUM ('PENDING', 'COMPLETED', 'FAILED', 'CANCELLED');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_phone VARCHAR(15) REFERENCES users(phone_number),
    to_phone VARCHAR(15) REFERENCES users(phone_number),
    amount DECIMAL(15,2) NOT NULL CHECK (amount > 0),
    transaction_type transaction_type NOT NULL,
    status transaction_status DEFAULT 'PENDING',
    description TEXT,
    reference_id VARCHAR(50),
    equb_account_id UUID REFERENCES equb_accounts(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

print("Setting up basic database tables...")

try:
    with engine.connect() as connection:
        connection.execute(text(basic_schema))
        connection.commit()
        print("✓ Basic tables created successfully!")
        
except Exception as e:
    print(f"✗ Setup failed: {e}")