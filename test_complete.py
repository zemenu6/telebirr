#!/usr/bin/env python3
import requests
import json
import time

# Test both local and deployed endpoints
LOCAL_URL = "http://localhost:8000"
DEPLOYED_URL = "https://federal-blisse-telebirr-56e12994.koyeb.app"

def test_telebirr_complete(base_url):
    print(f"\n=== Testing TeleBirr API: {base_url} ===")
    
    # Test 1: Health Check
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"✓ Health: {response.json()}")
    except Exception as e:
        print(f"✗ Health failed: {e}")
        return False
    
    # Test 2: Signup User 1
    user1_data = {
        "phoneNumber": "0911111111",
        "username": "Alice",
        "password": "pass11"
    }
    try:
        response = requests.post(f"{base_url}/auth/signup", json=user1_data, timeout=10)
        if response.status_code == 201 or response.status_code == 200:
            result = response.json()
            print(f"✓ User1 Signup: {result['message']}, Balance: {result.get('balance', 'N/A')}")
        elif response.status_code == 409:
            print("✓ User1 already exists")
        else:
            print(f"✗ User1 Signup failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ User1 Signup error: {e}")
    
    # Test 3: Signup User 2
    user2_data = {
        "phoneNumber": "0922222222",
        "username": "Bob",
        "password": "pass22"
    }
    try:
        response = requests.post(f"{base_url}/auth/signup", json=user2_data, timeout=10)
        if response.status_code == 201 or response.status_code == 200:
            result = response.json()
            print(f"✓ User2 Signup: {result['message']}, Balance: {result.get('balance', 'N/A')}")
        elif response.status_code == 409:
            print("✓ User2 already exists")
        else:
            print(f"✗ User2 Signup failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ User2 Signup error: {e}")
    
    # Test 4: Login User 1
    try:
        response = requests.post(f"{base_url}/auth/login", json=user1_data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ User1 Login: {result['message']}, Balance: {result.get('balance', 'N/A')}")
        else:
            print(f"✗ User1 Login failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ User1 Login error: {e}")
    
    # Test 5: Send Money (User1 to User2)
    send_data = {
        "recipientPhone": "0922222222",
        "amount": 100.50
    }
    try:
        response = requests.post(f"{base_url}/transactions/send-money", json=send_data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Send Money: {result['message']}, New Balance: {result.get('newBalance', 'N/A')}")
        else:
            print(f"✗ Send Money failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ Send Money error: {e}")
    
    # Test 6: Equb Deposit
    equb_data = {
        "phoneNumber": "0911111111",
        "amount": 500.00,
        "durationMonths": 1
    }
    try:
        response = requests.post(f"{base_url}/equb/deposit", json=equb_data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Equb Deposit: {result['message']}")
            equb_id = result.get('equbAccount', {}).get('id')
            if equb_id:
                print(f"  Equb ID: {equb_id}")
        else:
            print(f"✗ Equb Deposit failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ Equb Deposit error: {e}")
    
    # Test 7: Get Balance
    try:
        response = requests.get(f"{base_url}/user/balance?phoneNumber=0911111111", timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Balance Check: {result['balance']}, Equb Accounts: {len(result.get('equbAccounts', []))}")
        else:
            print(f"✗ Balance Check failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ Balance Check error: {e}")
    
    return True

def main():
    print("🚀 TeleBirr Complete Functionality Test")
    
    # Test local first
    print("\n📍 Testing LOCAL server...")
    test_telebirr_complete(LOCAL_URL)
    
    # Test deployed
    print("\n🌐 Testing DEPLOYED server...")
    test_telebirr_complete(DEPLOYED_URL)
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    main()