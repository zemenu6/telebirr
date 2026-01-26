-- TeleBirr Mobile Money App Database Schema
-- PostgreSQL Database for Nhost Backend

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table for authentication and account management
CREATE TABLE users (
    phone_number VARCHAR(15) PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    balance DECIMAL(15,2) DEFAULT 0.00 CHECK (balance >= 0),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Equb accounts table for traditional savings
CREATE TABLE equb_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone_number VARCHAR(15) NOT NULL REFERENCES users(phone_number) ON DELETE CASCADE,
    amount DECIMAL(15,2) NOT NULL CHECK (amount >= 500.00),
    deposit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    maturity_date TIMESTAMP NOT NULL,
    can_withdraw BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transaction types enum
CREATE TYPE transaction_type AS ENUM ('TRANSFER', 'EQUB_DEPOSIT', 'EQUB_WITHDRAWAL');

-- Transaction status enum
CREATE TYPE transaction_status AS ENUM ('PENDING', 'COMPLETED', 'FAILED', 'CANCELLED');

-- Transactions table for all money movements
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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

-- Session management table
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone_number VARCHAR(15) NOT NULL REFERENCES users(phone_number) ON DELETE CASCADE,
    session_token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit log table for security and compliance
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone_number VARCHAR(15) REFERENCES users(phone_number),
    action VARCHAR(100) NOT NULL,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance optimization
CREATE INDEX idx_users_phone ON users(phone_number);
CREATE INDEX idx_users_active ON users(is_active);
CREATE INDEX idx_equb_phone ON equb_accounts(phone_number);
CREATE INDEX idx_equb_active ON equb_accounts(is_active);
CREATE INDEX idx_equb_maturity ON equb_accounts(maturity_date);
CREATE INDEX idx_transactions_from ON transactions(from_phone);
CREATE INDEX idx_transactions_to ON transactions(to_phone);
CREATE INDEX idx_transactions_type ON transactions(transaction_type);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_date ON transactions(created_at);
CREATE INDEX idx_sessions_phone ON user_sessions(phone_number);
CREATE INDEX idx_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_audit_phone ON audit_logs(phone_number);
CREATE INDEX idx_audit_date ON audit_logs(created_at);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at columns
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_equb_updated_at BEFORE UPDATE ON equb_accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to automatically enable equb withdrawals when mature
CREATE OR REPLACE FUNCTION check_equb_maturity()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE equb_accounts 
    SET can_withdraw = TRUE 
    WHERE maturity_date <= CURRENT_TIMESTAMP 
    AND is_active = TRUE 
    AND can_withdraw = FALSE;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Trigger to check equb maturity on insert/update
CREATE TRIGGER equb_maturity_check
    AFTER INSERT OR UPDATE ON equb_accounts
    FOR EACH STATEMENT
    EXECUTE FUNCTION check_equb_maturity();

-- Function to validate Ethiopian phone numbers
CREATE OR REPLACE FUNCTION validate_ethiopian_phone(phone VARCHAR(15))
RETURNS BOOLEAN AS $$
BEGIN
    -- Check if phone starts with +251 or 251 or 09
    RETURN phone ~ '^(\+251|251|09)[0-9]{8,9}$';
END;
$$ LANGUAGE plpgsql;

-- Function to generate transaction reference
CREATE OR REPLACE FUNCTION generate_transaction_ref()
RETURNS VARCHAR(50) AS $$
BEGIN
    RETURN 'TB' || TO_CHAR(CURRENT_TIMESTAMP, 'YYYYMMDD') || 
           LPAD(FLOOR(RANDOM() * 999999)::TEXT, 6, '0');
END;
$$ LANGUAGE plpgsql;

-- Function to process money transfer
CREATE OR REPLACE FUNCTION process_money_transfer(
    sender_phone VARCHAR(15),
    recipient_phone VARCHAR(15),
    transfer_amount DECIMAL(15,2)
)
RETURNS JSONB AS $$
DECLARE
    sender_balance DECIMAL(15,2);
    transaction_id UUID;
    result JSONB;
BEGIN
    -- Start transaction
    BEGIN
        -- Check sender balance
        SELECT balance INTO sender_balance 
        FROM users 
        WHERE phone_number = sender_phone AND is_active = TRUE;
        
        IF sender_balance IS NULL THEN
            RETURN jsonb_build_object('success', false, 'message', 'Sender not found');
        END IF;
        
        IF sender_balance < transfer_amount THEN
            RETURN jsonb_build_object('success', false, 'message', 'Insufficient balance');
        END IF;
        
        -- Check recipient exists
        IF NOT EXISTS (SELECT 1 FROM users WHERE phone_number = recipient_phone AND is_active = TRUE) THEN
            RETURN jsonb_build_object('success', false, 'message', 'Recipient not found');
        END IF;
        
        -- Create transaction record
        INSERT INTO transactions (from_phone, to_phone, amount, transaction_type, reference_id, status)
        VALUES (sender_phone, recipient_phone, transfer_amount, 'TRANSFER', generate_transaction_ref(), 'COMPLETED')
        RETURNING id INTO transaction_id;
        
        -- Update balances
        UPDATE users SET balance = balance - transfer_amount WHERE phone_number = sender_phone;
        UPDATE users SET balance = balance + transfer_amount WHERE phone_number = recipient_phone;
        
        -- Get new sender balance
        SELECT balance INTO sender_balance FROM users WHERE phone_number = sender_phone;
        
        result := jsonb_build_object(
            'success', true,
            'message', 'Transfer successful',
            'transaction_id', transaction_id,
            'new_balance', sender_balance
        );
        
        RETURN result;
        
    EXCEPTION WHEN OTHERS THEN
        -- Update transaction status to failed
        UPDATE transactions SET status = 'FAILED' WHERE id = transaction_id;
        RETURN jsonb_build_object('success', false, 'message', 'Transfer failed: ' || SQLERRM);
    END;
END;
$$ LANGUAGE plpgsql;

-- Function to process equb deposit
CREATE OR REPLACE FUNCTION process_equb_deposit(
    user_phone VARCHAR(15),
    deposit_amount DECIMAL(15,2),
    duration_months INTEGER DEFAULT 1
)
RETURNS JSONB AS $$
DECLARE
    user_balance DECIMAL(15,2);
    equb_id UUID;
    maturity_date TIMESTAMP;
    result JSONB;
BEGIN
    BEGIN
        -- Validate minimum deposit
        IF deposit_amount < 500.00 THEN
            RETURN jsonb_build_object('success', false, 'message', 'Minimum deposit is 500 Birr');
        END IF;
        
        -- Check user balance
        SELECT balance INTO user_balance 
        FROM users 
        WHERE phone_number = user_phone AND is_active = TRUE;
        
        IF user_balance IS NULL THEN
            RETURN jsonb_build_object('success', false, 'message', 'User not found');
        END IF;
        
        IF user_balance < deposit_amount THEN
            RETURN jsonb_build_object('success', false, 'message', 'Insufficient balance');
        END IF;
        
        -- Calculate maturity date
        maturity_date := CURRENT_TIMESTAMP + INTERVAL '1 month' * duration_months;
        
        -- Create equb account
        INSERT INTO equb_accounts (phone_number, amount, maturity_date)
        VALUES (user_phone, deposit_amount, maturity_date)
        RETURNING id INTO equb_id;
        
        -- Create transaction record
        INSERT INTO transactions (from_phone, amount, transaction_type, reference_id, equb_account_id, status)
        VALUES (user_phone, deposit_amount, 'EQUB_DEPOSIT', generate_transaction_ref(), equb_id, 'COMPLETED');
        
        -- Update user balance
        UPDATE users SET balance = balance - deposit_amount WHERE phone_number = user_phone;
        
        -- Get new balance
        SELECT balance INTO user_balance FROM users WHERE phone_number = user_phone;
        
        result := jsonb_build_object(
            'success', true,
            'message', 'Equb deposit successful',
            'equb_id', equb_id,
            'maturity_date', maturity_date,
            'new_balance', user_balance
        );
        
        RETURN result;
        
    EXCEPTION WHEN OTHERS THEN
        RETURN jsonb_build_object('success', false, 'message', 'Deposit failed: ' || SQLERRM);
    END;
END;
$$ LANGUAGE plpgsql;

-- Function to process equb withdrawal
CREATE OR REPLACE FUNCTION process_equb_withdrawal(
    user_phone VARCHAR(15),
    equb_account_id UUID
)
RETURNS JSONB AS $$
DECLARE
    equb_amount DECIMAL(15,2);
    can_withdraw_flag BOOLEAN;
    user_balance DECIMAL(15,2);
    result JSONB;
BEGIN
    BEGIN
        -- Check equb account
        SELECT amount, can_withdraw INTO equb_amount, can_withdraw_flag
        FROM equb_accounts 
        WHERE id = equb_account_id 
        AND phone_number = user_phone 
        AND is_active = TRUE;
        
        IF equb_amount IS NULL THEN
            RETURN jsonb_build_object('success', false, 'message', 'Equb account not found');
        END IF;
        
        IF NOT can_withdraw_flag THEN
            RETURN jsonb_build_object('success', false, 'message', 'Equb not yet mature for withdrawal');
        END IF;
        
        -- Create transaction record
        INSERT INTO transactions (to_phone, amount, transaction_type, reference_id, equb_account_id, status)
        VALUES (user_phone, equb_amount, 'EQUB_WITHDRAWAL', generate_transaction_ref(), equb_account_id, 'COMPLETED');
        
        -- Update user balance
        UPDATE users SET balance = balance + equb_amount WHERE phone_number = user_phone;
        
        -- Deactivate equb account
        UPDATE equb_accounts SET is_active = FALSE WHERE id = equb_account_id;
        
        -- Get new balance
        SELECT balance INTO user_balance FROM users WHERE phone_number = user_phone;
        
        result := jsonb_build_object(
            'success', true,
            'message', 'Equb withdrawal successful',
            'amount', equb_amount,
            'new_balance', user_balance
        );
        
        RETURN result;
        
    EXCEPTION WHEN OTHERS THEN
        RETURN jsonb_build_object('success', false, 'message', 'Withdrawal failed: ' || SQLERRM);
    END;
END;
$$ LANGUAGE plpgsql;

-- Insert sample data for testing
INSERT INTO users (phone_number, username, password_hash, balance) VALUES
('+251911234567', 'John Doe', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/VJBzxqEyy', 5000.00),
('+251922345678', 'Jane Smith', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/VJBzxqEyy', 3000.00),
('+251933456789', 'Bob Johnson', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/VJBzxqEyy', 1500.00);

-- Create views for common queries
CREATE VIEW active_users AS
SELECT phone_number, username, balance, created_at
FROM users 
WHERE is_active = TRUE;

CREATE VIEW active_equb_accounts AS
SELECT ea.id, ea.phone_number, u.username, ea.amount, ea.deposit_date, ea.maturity_date, ea.can_withdraw
FROM equb_accounts ea
JOIN users u ON ea.phone_number = u.phone_number
WHERE ea.is_active = TRUE;

CREATE VIEW transaction_summary AS
SELECT 
    t.id,
    t.from_phone,
    t.to_phone,
    t.amount,
    t.transaction_type,
    t.status,
    t.reference_id,
    t.created_at,
    uf.username as from_username,
    ut.username as to_username
FROM transactions t
LEFT JOIN users uf ON t.from_phone = uf.phone_number
LEFT JOIN users ut ON t.to_phone = ut.phone_number
ORDER BY t.created_at DESC;

-- Grant permissions (adjust as needed for your Nhost setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO nhost_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO nhost_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO nhost_user;