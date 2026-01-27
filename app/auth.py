from typing import Optional
import jwt
import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from . import crud
from . import models
import os

# Nhost configuration
NHOST_GRAPHQL_URL = os.getenv("NHOST_GRAPHQL_URL", "https://mctmbhyqosnmbqorlhna.nhost.run/v1/graphql")
NHOST_HASURA_ADMIN_SECRET = os.getenv("NHOST_HASURA_ADMIN_SECRET", "d9e91e8f1e8c4e8b9e8c8e8c8e8c8e8c")
NHOST_JWT_ALGORITHM = "RS256"

security = HTTPBearer()

# Cache for Nhost public key
_nhost_public_key = None

def get_nhost_public_key():
    """Fetch Nhost's public key for JWT verification"""
    global _nhost_public_key
    if _nhost_public_key:
        return _nhost_public_key
    
    try:
        # Fetch JWKS from Nhost
        jwks_url = NHOST_GRAPHQL_URL.replace('/graphql', '/.well-known/jwks.json')
        response = requests.get(jwks_url)
        response.raise_for_status()
        jwks = response.json()
        
        # Extract the first key (Nhost typically uses one key)
        key_data = jwks['keys'][0]
        _nhost_public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key_data)
        return _nhost_public_key
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not fetch Nhost public key: {str(e)}"
        )




def verify_token_only(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token issued by Nhost"""
    token = credentials.credentials
    try:
        public_key = get_nhost_public_key()
        payload = jwt.decode(
            token, 
            public_key, 
            algorithms=[NHOST_JWT_ALGORITHM],
            audience=["authenticated"],
            issuer="https://mctmbhyqosnmbqorlhna.nhost.run"
        )
        
        # Extract user information from Nhost token
        user_metadata = payload.get("https://hasura.io/jwt/claims", {})
        phone_number = user_metadata.get("x-hasura-user-id") or payload.get("sub")
        
        if phone_number is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid token payload - no user ID found"
            )
        return phone_number
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=f"Could not validate token: {str(e)}"
        )


def get_current_user_with_db(phone_number: str = Depends(verify_token_only), db: Session = Depends(lambda: None)):
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database connection not available")
    user = crud.get_user_by_phone(db, phone_number)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


# Create a simple dependency that doesn't require db at import time
def get_current_user():
    def dependency(phone_number: str = Depends(verify_token_only), db: Session = Depends(lambda: None)):
        if db is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database connection not available")
        user = crud.get_user_by_phone(db, phone_number)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user
    return dependency


def sync_user_with_nhost(phone_number: str, db: Session):
    """Sync user from Nhost to local database"""
    try:
        # Check if user exists locally
        existing_user = crud.get_user_by_phone(db, phone_number)
        if existing_user:
            return existing_user
        
        # Create user in local database to match Nhost user
        # You might want to fetch additional user info from Nhost GraphQL API
        user = crud.create_user(
            db, 
            phone_number=phone_number, 
            username=f"user_{phone_number}",  # Default username
            password="",  # No password needed for Nhost users
            initial_balance=0.0
        )
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not sync user: {str(e)}"
        )
