#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("=== Testing TeleBirr API ===")
    
    # Test 1: Health check
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✓ Root endpoint: {response.json()}")
    except Exception as e:
        print(f"✗ Root endpoint failed: {e}")
    
    # Test 2: Health endpoint
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✓ Health endpoint: {response.json()}")
    except Exception as e:
        print(f"✗ Health endpoint failed: {e}")
    
    # Test 3: Signup with proper Ethiopian format
    signup_data = {
        "phoneNumber": "0912345678",
        "username": "Test User",
        "password": "test12"
    }
    try:
        response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
        print(f"✓ Signup: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"✗ Signup failed: {e}")

if __name__ == "__main__":
    test_api()