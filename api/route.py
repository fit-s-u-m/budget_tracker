from custom_types import TransactionRequest
from core.database import fetch_current_balance,fetch_monthly_spending_summary,fetch_transactions_for_user,insert_transaction, verify_otp,search_transactions,count_total_transactions

import os
from bots.bot import init_bot
from dotenv import load_dotenv
import getpass
from core.database import initalize_tables
from telegram import Update
from typing import Optional

from fastapi import FastAPI,Request,Query,HTTPException
from fastapi.middleware.cors import CORSMiddleware

import logging

load_dotenv()
if "TELEGRAM_API_KEY" not in os.environ:
    os.environ["TELEGRAM_API_KEY"] = getpass.getpass("Enter your Telegram bot token key: ")

TOKEN = os.environ["TELEGRAM_API_KEY"]

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
    telegram_app = init_bot(TOKEN)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def startup():
        initalize_tables()
        await telegram_app.initialize()
        await telegram_app.bot.set_webhook(
            url=f"{os.environ['WEBHOOK_URL']}/telegram/webhook"
    )

    @app.post("/telegram/webhook")
    async def telegram_webhook(request: Request):
        data = await request.json()
        update = Update.de_json(data, telegram_app.bot)
        await telegram_app.process_update(update)
        return {"ok": True}


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
        print(transactions)
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
    async def add_transaction(txn: TransactionRequest):
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
        transaction_id = await insert_transaction(
            account_id=txn.account_id,
            amount=txn.amount,
            reason=txn.reason,
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

    @app.get("/transactions/search")
    def search_transactions_route(
        telegram_id: str = Query(..., description="Telegram user id"),
        text: Optional[str] = Query(None, description="Search in reason"),
        category_id: Optional[int] = Query(None),
        created_at:Optional[str]=Query(None,description="Date in YYYY-MM-DD format"),
        tx_type: Optional[str] = Query(None, regex="^(income|expense)$"),
        limit: int = Query(50, ge=1, le=100),
        offset: int = Query(0, ge=0),
    ):
        try:
            results = search_transactions(
                telegram_id=telegram_id,
                text=text,
                category_id=category_id,
                created_at=created_at,
                tx_type=tx_type,
                limit=limit,
                offset=offset,
            )
            print("result from search: - ",results)

            response = [
                {
                    "id": x[0],
                    "amount": x[1],
                    "type": x[2],
                    "description": x[3],
                    "date": x[4],
                    "account_name": x[5],
                    "category": x[6],
                }
                for x in results
            ]
            return  response
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/transactions/count")
    def count_transactions():
        count_total = count_total_transactions()
        return {"total": count_total}

    return app
