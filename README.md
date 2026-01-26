# TeleBirr Mobile Money App

<div align="center">
  <img src="https://img.shields.io/badge/Platform-FastAPI-green.svg" alt="Platform">
  <img src="https://img.shields.io/badge/Language-Python-blue.svg" alt="Language">
  <img src="https://img.shields.io/badge/Database-PostgreSQL-orange.svg" alt="Database">
  <img src="https://img.shields.io/badge/Hosting-Nhost-purple.svg" alt="Hosting">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</div>

## 📱 Overview

TeleBirr is a comprehensive mobile money application designed for Ethiopian users, featuring traditional **Equb** savings system alongside modern digital payment capabilities. This FastAPI backend provides the complete server-side infrastructure with Nhost PostgreSQL database integration.

## ✨ Key Features

### 🔐 Authentication
- **Phone Number Login**: Ethiopian phone number format (+251)
- **Secure Registration**: Full name, phone validation, password confirmation
- **Password Security**: Minimum 6 characters with bcrypt hashing
- **JWT Tokens**: Secure token-based authentication

### 💸 Money Transfer
- **Phone-to-Phone Transfers**: Send money using recipient's phone number
- **Real-time Validation**: Input validation and balance checks
- **Transaction Confirmation**: Secure transfer confirmation
- **Atomic Operations**: Database-level transaction consistency

### 🏦 Equb Services (Traditional Savings)
- **Minimum Deposit**: 500 Birr requirement
- **Lock Period**: Exactly 1 month from deposit date
- **Multiple Accounts**: Users can have multiple active equb savings
- **Withdrawal Restrictions**: Money locked until maturity date
- **Automatic Maturity**: System tracks and enables withdrawals

### 🔒 Security & Compliance
- **Ethiopian Phone Validation**: +251 format validation
- **Password Hashing**: Secure bcrypt implementation
- **Audit Logging**: Complete transaction history
- **Session Management**: Secure token-based authentication
- **Input Validation**: Comprehensive request validation

## 🏗️ Technical Stack

### Backend (FastAPI + Nhost)
- **Framework**: FastAPI with Python
- **Database**: PostgreSQL with comprehensive schema
- **Authentication**: Phone-based with JWT tokens
- **Business Logic**: Stored procedures for transactions
- **Security**: Input validation and audit logging
- **Hosting**: Nhost serverless functions

### Database Features
- **Users**: Phone authentication and balance management
- **Equb Accounts**: Traditional savings with maturity tracking
- **Transactions**: All money movements with status tracking
- **Audit Logs**: Security and compliance logging
- **Stored Procedures**: Atomic transaction processing

## 📊 Database Schema

Complete database schema available in `schema.sql` with:
- **Users Table**: Phone number primary key, balance tracking
- **Equb Accounts**: UUID-based accounts with maturity dates
- **Transactions**: Complete transaction history with types
- **Session Management**: JWT token tracking
- **Audit Logs**: Security and compliance logging

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/zemenu6/telebirr.git
cd telebirr
```

### 2. Setup Nhost Project
1. **Create Nhost Account**: Go to [Nhost Dashboard](https://app.nhost.io)
2. **Create New Project**: Click "New Project" → Choose region
3. **Get Database Credentials**: Navigate to **Database** → **Connection parameters**

### 3. Configure Environment
Update the `.env` file with your actual Nhost credentials:

```bash
# Nhost Database Configuration
NHOST_DB_HOST=mctmbhyqosnmbqorlhna.db.eu-central-1.nhost.run
NHOST_DB_PORT=5432
NHOST_DB_USER=postgres
NHOST_DB_PASSWORD=1dBufXeykxdVBsrJ
NHOST_DB_NAME=mctmbhyqosnmbqorlhna

# JWT Secret from Nhost dashboard → Settings → Authentication → JWT Secret
NHOST_JWT_SECRET=your-actual-jwt-secret-here

# Webhook Secret from Nhost dashboard → Settings → Functions → Webhook Secret
NHOST_WEBHOOK_SECRET=your-actual-webhook-secret-here

# Constructed Database URL (used by the application)
DATABASE_URL=postgresql://${NHOST_DB_USER}:${NHOST_DB_PASSWORD}@${NHOST_DB_HOST}:${NHOST_DB_PORT}/${NHOST_DB_NAME}
SECRET_KEY=${NHOST_JWT_SECRET}

# Production Environment
ENVIRONMENT=production
```

### 4. Setup Database
Run the database schema in your Nhost PostgreSQL:

```bash
# Option 1: Using psql
psql -h mctmbhyqosnmbqorlhna.db.eu-central-1.nhost.run -U postgres -d mctmbhyqosnmbqorlhna -f schema.sql

# Option 2: Using Nhost Dashboard
# Navigate to Database → SQL Editor → Paste schema.sql content → Execute
```

### 5. Install Dependencies
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 6. Run Backend Locally
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Deploy to Production

#### Option A: Nhost Functions (Recommended)
```bash
npm install -g @nhost/cli
nhost login
nhost functions deploy
```

#### Option B: Koyeb (Serverless)
1. Connect GitHub repository to Koyeb
2. Use `koyeb.yaml` configuration
3. Deploy automatically

#### Option C: Docker
```bash
docker build -t telebirr .
docker run -p 8000:8000 telebirr
```

## 🔧 Technical Configuration

### Database Connection Details

#### Nhost PostgreSQL Connection
```bash
# Connection String
postgresql://postgres:1dBufXeykxdVBsrJ@mctmbhyqosnmbqorlhna.db.eu-central-1.nhost.run:5432/mctmbhyqosnmbqorlhna

# Individual Parameters
Host: mctmbhyqosnmbqorlhna.db.eu-central-1.nhost.run
Port: 5432
Database: mctmbhyqosnmbqorlhna
Username: postgres
Password: 1dBufXeykxdVBsrJ
```

#### Environment Variables
| Variable | Value | Description |
|----------|-------|-------------|
| `DATABASE_URL` | Full PostgreSQL connection string | Database connection |
| `SECRET_KEY` | JWT secret from Nhost | JWT token signing |
| `ENVIRONMENT` | `production` | App environment |
| `NHOST_DB_HOST` | `mctmbhyqosnmbqorlhna.db.eu-central-1.nhost.run` | Database host |
| `NHOST_DB_PORT` | `5432` | Database port |
| `NHOST_DB_USER` | `postgres` | Database username |
| `NHOST_DB_PASSWORD` | `1dBufXeykxdVBsrJ` | Database password |
| `NHOST_DB_NAME` | `mctmbhyqosnmbqorlhna` | Database name |

### API Endpoints

#### Base URLs
- **Local Development**: `http://localhost:8000`
- **Nhost Production**: `https://mctmbhyqosnmbqorlhna.functions.nhost.run`
- **Koyeb Production**: `https://telebirr-username.koyeb.app`

#### Authentication Endpoints
```bash
# User Registration
POST /auth/signup
{
    "phoneNumber": "+251912345678",
    "username": "John Doe",
    "password": "password123"
}

# User Login
POST /auth/login
{
    "phoneNumber": "+251912345678",
    "password": "password123"
}
```

#### Money Transfer Endpoints
```bash
# Send Money (requires JWT token)
POST /transactions/send-money
Headers: Authorization: Bearer <jwt_token>
{
    "recipientPhone": "+251987654321",
    "amount": 100.00
}

# Check Balance
GET /user/balance?phoneNumber=+251912345678
Headers: Authorization: Bearer <jwt_token>
```

#### Equb Savings Endpoints
```bash
# Deposit to Equb
POST /equb/deposit
Headers: Authorization: Bearer <jwt_token>
{
    "phoneNumber": "+251912345678",
    "amount": 500.00,
    "durationMonths": 1
}

# Withdraw from Equb
POST /equb/withdraw
Headers: Authorization: Bearer <jwt_token>
{
    "phoneNumber": "+251912345678",
    "equbAccountId": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Database Schema Structure

#### Core Tables
```sql
-- Users Table (Phone-based authentication)
CREATE TABLE users (
    phone_number VARCHAR(15) PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    balance DECIMAL(15,2) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Equb Accounts (Traditional savings)
CREATE TABLE equb_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone_number VARCHAR(15) NOT NULL REFERENCES users(phone_number),
    amount DECIMAL(15,2) NOT NULL CHECK (amount >= 500.00),
    deposit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    maturity_date TIMESTAMP NOT NULL,
    can_withdraw BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE
);

-- Transactions (All money movements)
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_phone VARCHAR(15) REFERENCES users(phone_number),
    to_phone VARCHAR(15) REFERENCES users(phone_number),
    amount DECIMAL(15,2) NOT NULL,
    transaction_type transaction_type NOT NULL,
    status transaction_status DEFAULT 'PENDING',
    description TEXT,
    reference_id VARCHAR(50),
    equb_account_id UUID REFERENCES equb_accounts(id)
);
```

### Security Configuration

#### JWT Authentication
```python
# JWT Configuration
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ALGORITHM = "HS256"
SECRET_KEY = "your-nhost-jwt-secret"

# Token Creation
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

#### Password Security
```python
# Password Hashing
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash Password
hashed_password = pwd_context.hash(password)

# Verify Password
verified = pwd_context.verify(plain_password, hashed_password)
```

### Deployment Configurations

#### Nhost Functions Configuration
```yaml
# nhost.yaml (if using Nhost)
functions:
  - name: telebirr-api
    path: .
    runtime: python39
    memory: 512
    timeout: 30
```

#### Koyeb Configuration
```yaml
# koyeb.yaml
name: telebirr
services:
  - name: api
    type: web
    port: 8000
    build:
      type: docker
      dockerfile: Dockerfile
    env:
      - key: DATABASE_URL
        value: postgresql://postgres:1dBufXeykxdVBsrJ@mctmbhyqosnmbqorlhna.db.eu-central-1.nhost.run:5432/mctmbhyqosnmbqorlhna
      - key: SECRET_KEY
        value: changeme
      - key: ENVIRONMENT
        value: production
```

#### Docker Configuration
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Testing Configuration

#### Local Testing
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Test specific endpoint
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"phoneNumber": "+251912345678", "username": "Test User", "password": "testpass123"}'
```

#### Production Testing
```bash
# Test deployed API
curl -X POST https://your-deployment-url/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"phoneNumber": "+251912345678", "username": "Test User", "password": "testpass123"}'
```

### Monitoring & Health Checks

#### Health Check Endpoint
```bash
GET /
# Response: {"message": "TeleBirr API is running"}
```

#### Database Health
```bash
# Test database connection
curl -X GET http://localhost:8000/health/db
# Response: {"database": "connected", "status": "healthy"}
```

#### Monitoring Tools
- **Nhost Dashboard**: Built-in monitoring and logs
- **Koyeb Dashboard**: Instance metrics and logs
- **Local**: Use `uvicorn` logs for debugging

### Troubleshooting

#### Common Issues
1. **Database Connection Failed**
   - Check DATABASE_URL format
   - Verify Nhost credentials
   - Ensure database is running

2. **JWT Token Errors**
   - Verify SECRET_KEY is set
   - Check token expiration
   - Ensure proper Authorization header

3. **Deployment Failures**
   - Check requirements.txt versions
   - Verify environment variables
   - Review deployment logs

#### Debug Commands
```bash
# Check database connection
python -c "from app.main import engine; print(engine.execute('SELECT 1').scalar())"

# Test JWT creation
python -c "from app.auth import create_access_token; print(create_access_token({'sub': '+251912345678'}))"

# Verify imports
python -c "from app import models, crud, schemas, auth, exceptions; print('All imports successful')"
```

## 📱 Backend Structure

```
telebirr/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── models.py               # SQLAlchemy ORM models
│   ├── schemas.py              # Pydantic request/response schemas
│   ├── crud.py                 # Database operations (CRUD)
│   ├── auth.py                 # JWT authentication logic
│   └── exceptions.py           # Custom error handlers
├── schema.sql                  # Complete database schema
├── requirements.txt            # Python dependencies
├── .env                       # Environment variables
├── Dockerfile                 # Docker configuration
├── koyeb.yaml                 # Koyeb deployment config
├── Procfile                   # Heroku-style process definition
├── runtime.txt                # Python version specification
└── README.md                  # This comprehensive guide
```

## 🎯 Equb Business Rules

### ✅ Deposit Rules
- **Minimum Amount**: 500 Birr
- **Lock Period**: Exactly 1 month from deposit date
- **Multiple Accounts**: Users can have multiple active equb savings
- **Automatic Maturity**: System tracks and enables withdrawals

### ✅ Withdrawal Rules
- **Maturity Required**: Available only after maturity date
- **Full Withdrawal**: Complete amount withdrawal only
- **Account Deactivation**: Account closes after withdrawal
- **User Selection**: Users choose from matured accounts

## 🔒 Security Features

- **Ethiopian Phone Validation**: +251 format validation
- **Password Hashing**: Secure bcrypt implementation
- **JWT Authentication**: Token-based security
- **Atomic Transactions**: Database-level consistency
- **Input Validation**: Comprehensive request validation
- **CORS Protection**: Proper cross-origin configuration

## 🚀 Production Checklist

### Before Deployment
- [ ] Update environment variables with actual credentials
- [ ] Run database schema in production database
- [ ] Test all API endpoints locally
- [ ] Verify JWT authentication works
- [ ] Check database connectivity
- [ ] Test error handling

### After Deployment
- [ ] Verify health check endpoint
- [ ] Test API with real phone numbers
- [ ] Monitor application logs
- [ ] Set up monitoring alerts
- [ ] Test money transfer functionality
- [ ] Verify equb deposit/withdrawal

---

<div align="center">
  <p><strong>Built with ❤️ for Ethiopia</strong></p>
  <p>TeleBirr Backend - Empowering Digital Payments & Traditional Savings</p>
  <p>
    <img src="https://img.shields.io/badge/FastAPI-0.104.1-green.svg" alt="FastAPI">
    <img src="https://img.shields.io/badge/PostgreSQL-15-blue.svg" alt="PostgreSQL">
    <img src="https://img.shields.io/badge/Nhost-Serverless-purple.svg" alt="Nhost">
  </p>
</div>

## 🎯 Equb Business Rules

### ✅ Deposit Rules
- Minimum: **500 Birr**
- Duration: **1 month lock period**
- Multiple deposits allowed
- Automatic maturity tracking

### ✅ Withdrawal Rules
- Available only after maturity
- Full amount withdrawal
- Account deactivation after withdrawal
- User selection from mature accounts

## 📚 API Documentation

### Authentication Endpoints

#### `POST /auth/signup`
Create a new user account with phone number authentication.

**Request:**
```json
{
    "phoneNumber": "+251912345678",
    "username": "John Doe",
    "password": "password123"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Account created successfully",
    "phoneNumber": "+251912345678",
    "username": "John Doe",
    "balance": "0.00"
}
```

#### `POST /auth/login`
Authenticate user and return user information.

**Request:**
```json
{
    "phoneNumber": "+251912345678",
    "password": "password123"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Login successful",
    "phoneNumber": "+251912345678",
    "username": "John Doe",
    "balance": "1500.00"
}
```

### Money Transfer Endpoints

#### `POST /transactions/send-money`
Send money to another user (requires JWT token).

**Request:**
```json
{
    "recipientPhone": "+251987654321",
    "amount": 100.00
}
```

**Response:**
```json
{
    "success": true,
    "message": "Money sent successfully",
    "transactionId": "550e8400-e29b-41d4-a716-446655440000",
    "newBalance": "1400.00"
}
```

### Equb Savings Endpoints

#### `POST /equb/deposit`
Deposit money into equb savings account (requires JWT token).

**Request:**
```json
{
    "phoneNumber": "+251912345678",
    "amount": 500.00,
    "durationMonths": 1
}
```

**Response:**
```json
{
    "success": true,
    "message": "Equb deposit successful",
    "equbAccount": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "phoneNumber": "+251912345678",
        "amount": "500.00",
        "depositDate": "2024-01-15T10:30:00Z",
        "maturityDate": "2024-02-15T10:30:00Z",
        "canWithdraw": false,
        "isActive": true
    }
}
```

#### `POST /equb/withdraw`
Withdraw from matured equb account (requires JWT token).

**Request:**
```json
{
    "phoneNumber": "+251912345678",
    "equbAccountId": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Equb withdrawal successful",
    "transactionId": "550e8400-e29b-41d4-a716-446655440001",
    "newBalance": "2000.00"
}
```

## 📱 Backend Structure

```
telebirr-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── crud.py                 # Database operations
│   ├── auth.py                 # JWT authentication
│   └── exceptions.py           # Error handling
├── schema.sql                  # Complete database schema
├── requirements.txt            # Python dependencies
├── .env                       # Environment configuration
└── README.md                  # This file
```

## 🔒 Security Features

- **Ethiopian Phone Validation**: +251 format validation
- **Password Hashing**: Secure bcrypt implementation
- **JWT Authentication**: Token-based security
- **Atomic Transactions**: Database-level consistency
- **Audit Logging**: Complete transaction history
- **Input Validation**: Comprehensive request validation
- **CORS Protection**: Proper cross-origin configuration

## ⚠️ Error Handling

All errors follow a consistent format:

```json
{
    "success": false,
    "message": "Human-readable error description",
    "error_code": "MACHINE_READABLE_CODE"
}
```

### Common Error Codes
| Error Code | Description |
|------------|-------------|
| `INSUFFICIENT_FUNDS` | Not enough balance for transaction |
| `INVALID_PHONE` | Invalid phone number format |
| `EQUB_NOT_MATURE` | Equb account not ready for withdrawal |
| `MINIMUM_DEPOSIT` | Below 500 Birr minimum requirement |
| `USER_NOT_FOUND` | User account does not exist |
| `TOKEN_MISMATCH` | JWT token doesn't match request |

## 🧪 Testing

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest

# Run with coverage
pytest --cov=app
```

### Example Test Cases
```python
# Test user registration
def test_signup():
    response = client.post("/auth/signup", json={
        "phoneNumber": "+251912345678",
        "username": "Test User",
        "password": "testpass123"
    })
    assert response.status_code == 200
    assert response.json()["success"] == True
```

## 🚀 Deployment

### Nhost Functions Deployment (Recommended)

1. **Install Nhost CLI:**
```bash
npm install -g @nhost/cli
```

2. **Login to Nhost:**
```bash
nhost login
```

3. **Deploy as Nhost Function:**
```bash
nhost functions deploy
```

The API will be available at:
- **Local Development**: `http://localhost:8000` (connected to Nhost database)
- **Nhost Production**: `https://<your-project-name>.functions.nhost.run`

## 📈 Monitoring & Logging

### Health Check
```bash
GET /
# Returns: {"message": "TeleBirr API is running"}
```

### Nhost Monitoring
Nhost provides built-in monitoring tools:
- **Function Logs**: Real-time logs in Nhost dashboard
- **Database Monitoring**: PostgreSQL performance metrics
- **Error Tracking**: Automatic error collection and alerts
- **Usage Analytics**: API call statistics and usage patterns

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 📞 Support

- 📧 Email: support@telebirr-app.com
- 📱 Phone: +251-XXX-XXX-XXX
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/telebirr-backend/issues)
- 📚 Documentation: [TeleBirr API Docs](https://docs.telebirr.com)

## 🗺️ Roadmap

- [ ] Mobile app integration
- [ ] SMS notification system via Nhost
- [ ] Advanced analytics dashboard
- [ ] Multi-currency support
- [ ] Webhook integrations
- [ ] Rate limiting and throttling
- [ ] Redis caching layer with Nhost
- [ ] Microservices architecture
- [ ] GraphQL API support
- [ ] Real-time notifications with Nhost subscriptions

---

<div align="center">
  <p><strong>Built with ❤️ for Ethiopia</strong></p>
  <p>TeleBirr Backend - Empowering Digital Payments & Traditional Savings</p>
  <p>
    <img src="https://img.shields.io/badge/FastAPI-0.104.1-green.svg" alt="FastAPI">
    <img src="https://img.shields.io/badge/PostgreSQL-15-blue.svg" alt="PostgreSQL">
    <img src="https://img.shields.io/badge/Nhost-Serverless-purple.svg" alt="Nhost">
  </p>
</div>
