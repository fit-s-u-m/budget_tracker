import requests
import json
import asyncio
import websockets
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws/transactions"

# Use a consistent telegram_id for testing
TEST_TELEGRAM_ID = 123456789

def test_root():
    print("--- Testing Root ---")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Response: {response.json()}")
        assert response.status_code == 200
    except Exception as e:
        print(f"FAILED: Root test: {e}")

def test_balance():
    print("\n--- Testing /balance ---")
    params = {"telegram_id": TEST_TELEGRAM_ID}
    try:
        response = requests.get(f"{BASE_URL}/balance", params=params)
        print(f"Response: {response.json()}")
        assert response.status_code == 200
    except Exception as e:
        print(f"FAILED: Balance test: {e}")

def test_transactions_list():
    print("\n--- Testing /trasactions (Checking for typo in codebase) ---")
    params = {"limit": 5, "telegram_id": TEST_TELEGRAM_ID}
    try:
        # Note: The codebase currently uses /trasactions (missing 'n')
        response = requests.get(f"{BASE_URL}/trasactions", params=params)
        if response.status_code == 200:
            print(f"SUCCESS: Found {len(response.json())} transactions")
        else:
            print(f"FAILED: Status {response.status_code}, {response.text}")
    except Exception as e:
        print(f"FAILED: Transactions list test: {e}")

def test_monthly_summary():
    print("\n--- Testing /monthly_summary ---")
    params = {"telegram_id": TEST_TELEGRAM_ID}
    try:
        response = requests.get(f"{BASE_URL}/monthly_summary", params=params)
        print(f"Response: {response.json()}")
        assert response.status_code == 200
    except Exception as e:
        print(f"FAILED: Monthly summary test: {e}")

def test_transactions_count():
    print("\n--- Testing /transactions/count ---")
    try:
        response = requests.get(f"{BASE_URL}/transactions/count")
        print(f"Response: {response.json()}")
        assert response.status_code == 200
    except Exception as e:
        print(f"FAILED: Transactions count test: {e}")

async def test_websocket_and_transaction():
    print("\n--- Testing Websocket Broadcast and Add Transaction ---")
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("Connected to Websocket")
            
            # Add a transaction via API
            payload = {
                "telegram_id": TEST_TELEGRAM_ID,
                "amount": 42.0,
                "category": "Test-Category",
                "type_": "debit",
                "reason": "Websocket Test Transaction",
                "created_at": datetime.now().isoformat()
            }
            print(f"Adding transaction via POST /transaction: {payload['reason']}")
            response = requests.post(f"{BASE_URL}/transaction", json=payload)
            print(f"API Response: {response.json()}")
            
            # Wait for websocket broadcast
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"Websocket Received: {data}")
                if data.get("action") == "new_transaction" and float(data.get("amount")) == 42.0:
                    print("SUCCESS: Transaction broadcast received correctly!")
                else:
                    print(f"FAILED: Unexpected message: {data}")
            except asyncio.TimeoutError:
                print("FAILED: Websocket timeout: No broadcast received")
    except Exception as e:
        print(f"FAILED: Websocket/Transaction test: {e}")

def test_verify_otp():
    print("\n--- Testing /verify_otp (GET) ---")
    try:
        # Note: This is a GET request in the code. Testing route availability.
        response = requests.get(f"{BASE_URL}/verify_otp", params={"entered_otp": "000000"})
        print(f"Response: {response.json()}")
        assert response.status_code == 200
    except Exception as e:
        print(f"FAILED: OTP verification test: {e}")

def run_tests():
    test_root()
    test_balance()
    test_transactions_list()
    test_monthly_summary()
    test_transactions_count()
    test_verify_otp()
    
    try:
        asyncio.run(test_websocket_and_transaction())
    except Exception as e:
        print(f"Async tests failed: {e}")

if __name__ == "__main__":
    print("==========================================")
    print("   Budget Tracker Flow Test Script        ")
    print("==========================================")
    print(f"Target API: {BASE_URL}")
    print("Note: Ensure the backend is running before starting.")
    print("Usage: python scripts/test_flow.py\n")
    
    run_tests()
    print("\n==========================================")
    print("   Tests Completed                        ")
    print("==========================================")
