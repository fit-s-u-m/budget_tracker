from custom_types import TransactionRequest
from core.database import fetch_current_balance,fetch_monthly_spending_summary,fetch_transactions_for_user,insert_transaction, verify_otp


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import logging

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Create a logger instance
logger = logging.getLogger(__name__)
def create_app() -> FastAPI:
    app = FastAPI()
    origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


    @app.get("/")
    def read_root():
        return {"message": "Budget Tracker API is running."}
    @app.get("/balance")
    def get_balance(account_id: int,telegram_id: int):
        """
        Get current balance for an account
        Example: GET /balance?account_id=20&telegram_id=123456
        """
        balance = fetch_current_balance(account_id,telegram_id)
        return {"account_id": account_id, "telegram_id": telegram_id, "balance": balance}

    @app.get("/trasactions")
    def get_transactions(limit: int,telegram_id: int):
        """
        Get recent transactions for a user
        Example: GET /transactions?limit=10&telegram_id=123456
        """
        transactions = fetch_transactions_for_user(telegram_id = telegram_id, limit = limit)
        return transactions

    @app.get("/monthly_summary")
    def get_monthly_summary(telegram_id: int):
        """
        Get monthly spending summary for a user
        Example: GET /monthly_summary?telegram_id=123456
        """
        summary = fetch_monthly_spending_summary(telegram_id = telegram_id)
        return summary
    
    @app.post("/transaction")
    def add_transaction(txn: TransactionRequest):
        """
        Add a new transaction for a user using JSON body:
        {
            "account_id":20,
            "amount":50.0,
            "category":"Food",
            "type_":"debit",
            "reason":"for lunch",
            "created_at":"2024-10-01T12:00:00"
        }
        """
        transaction_id = insert_transaction(
            account_id=txn.account_id,
            amount=txn.amount,
            reason=txn.reason,
            created_at=txn.created_at,
            category_name=txn.category,
            type=txn.type_,
        )
        return {"transaction_id": transaction_id, "status": "success"}
    @app.get("/verify_otp")
    def varify_otp(entered_otp: str):
        """
        Verify OTP for a user
        Example: POST /verify_otp with JSON body {"entered_otp":"ABC123"}
        """
        print("Verifying OTP:", entered_otp)
        logger.info(f"Verifying OTP: {entered_otp}")
        resp = verify_otp(entered_otp)
        if resp is not None:
            telgram_id, account_id = resp
            print(resp)
            return {"telegram_id": telgram_id, "account_id": account_id, "status": "verified"}
        return {"status": "invalid OTP"}
    return app
