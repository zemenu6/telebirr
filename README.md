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
git clone https://github.com/yourusername/telebirr-backend.git
cd telebirr-backend
```

### 2. Setup Nhost Project
- Go to [Nhost Dashboard](https://app.nhost.io)
- Create a new project or use existing one
- Navigate to **Database** → **Connection parameters**

### 3. Configure Environment
Update the `.env` file with your Nhost credentials:
```bash
# Nhost Database Configuration
NHOST_DB_HOST=your-project-name.db.nhost.run
NHOST_DB_PORT=5432
NHOST_DB_USER=postgres
NHOST_DB_PASSWORD=your-actual-password-here
NHOST_DB_NAME=postgres

# JWT Secret from Nhost dashboard
NHOST_JWT_SECRET=your-actual-jwt-secret-here
```

### 4. Setup Database
```bash
# Run schema.sql in your Nhost PostgreSQL database
psql -h your-nhost-db.nhost.run -U postgres -d postgres -f schema.sql
```

### 5. Install Dependencies
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 6. Run Backend
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Deploy to Nhost
```bash
npm install -g @nhost/cli
nhost login
nhost functions deploy
```

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
