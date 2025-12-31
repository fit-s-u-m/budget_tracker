import sqlite3
from queries import (
    create_query, 
    insert_query,
    update_query,
    get_query,
)
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import random
import psycopg
from dotenv import load_dotenv
import os
import asyncio
from api.websocket import manager

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg.connect(DATABASE_URL)


# Initialize the database and create tables if they do not exist
def initalize_tables():
    with get_conn() as connection:
        cursor = connection.cursor()

        cursor.execute(create_query.create_user_table)
        cursor.execute(create_query.create_account_table)
        cursor.execute(create_query.create_category_table)
        cursor.execute(create_query.create_index)
        cursor.execute(create_query.create_transaction_table)
        cursor.execute(create_query.create_otp_codes)

        connection.commit()
        print("Tables created successfully.")

# Insert a new user into the users table
def insert_user(telegram_id, name):
    with get_conn() as connection:
        cursor = connection.cursor()

        cursor.execute(insert_query.insert_user_query, (telegram_id, name))
        
        cursor.execute(
            "SELECT id, telegram_id, name FROM users WHERE telegram_id = %s",
            (telegram_id,),
        )
        user_info = cursor.fetchone()

        connection.commit()
        print(f"User inserted successfully.info: {user_info}")
        return user_info

async def insert_transaction(account_id: int, category_name: str, amount:int, type:str, reason:str):
    # print("")
    with get_conn() as connection:
        with connection.cursor() as cursor:
            if amount <= 0:
                raise ValueError("Amount must be a positive integer.")
            # Insert category
            cursor.execute(insert_query.insert_category_query, (category_name, type))
            category = cursor.fetchone()
            if category is None:
                # Category already exists, fetch it
                cursor.execute("SELECT id, name, type FROM categories WHERE name = %s", (category_name,))
                category = cursor.fetchone()
            print(category,category_name)
            category_id = category[0] if category else None

            # Insert transaction
            cursor.execute(
                insert_query.insert_transaction_query,
                (account_id, category_id, amount, type, reason)
            )
            transaction = cursor.fetchone()
            transaction_id = transaction[0] if transaction else None

            print(f"Transaction inserted successfully.id: {transaction_id}")

            # Update balance
            if type == "debit":
                cursor.execute(update_query.subtract_balance_query, (amount, account_id))
            elif type == "credit":
                cursor.execute(update_query.add_balance_query, (amount, account_id))

            asyncio.create_task(manager.broadcast({
                "action": "new_transaction",
                "transaction_id": transaction_id,
                "account_id": account_id,
                "category": category_name,
                "amount": amount,
                "type": type,
                "reason": reason,
            }))

            connection.commit()
            return transaction_id

# Create a new category in the categories table
def create_category(name, type):
    with get_conn() as connection:
        cursor = connection.cursor()

        cursor.execute(insert_query.insert_category_query, (name, type))

        connection.commit()
        category = cursor.fetchone()
        category_id = category[0] if category else None
        print(f"Category inserted successfully.{category_id}")
        return category_id

# Create a new account in the accounts table
def create_account(telegram_id, name):
    with get_conn() as connection:
        cursor = connection.cursor()

        cursor.execute(insert_query.insert_account_query, (telegram_id, name))
        cursor.execute(
            "SELECT id FROM accounts WHERE telegram_id = %s",
            (telegram_id,)
        )
        account = cursor.fetchone()
        account_id = account[0]


        connection.commit()
        print("Account inserted successfully.", account_id)
        return account_id
def fetch_accounts_by_telegram_id(telegram_id: int) -> List[Dict]:
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(get_query.get_accounts_by_telegram_id_query, (telegram_id,))
        rows = cursor.fetchall()
    return [{"id": r[0], "name": r[1], "balance": r[2], "created_at": r[3]} for r in rows]

def fetch_all_accounts_with_balance(telegram_id: int) -> List[Dict]:
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(get_query.get_all_accounts_with_balance_query, (telegram_id,))
        rows = cursor.fetchall()
    return [{"id": r[0], "name": r[1], "balance": r[2]} for r in rows]

def fetch_current_balance(account_id: int, telegram_id: int) -> int:
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(get_query.get_current_balance_query, (account_id, telegram_id))
        row = cursor.fetchone()
    return row[0] if row else 0

# ---------------- TRANSACTIONS ----------------
def fetch_transactions_for_user(telegram_id: int,limit: Optional[int] = None) -> List[Dict]:
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(get_query.get_account_transactions_query, (telegram_id,))
        if limit is not None:
            rows = cursor.fetchmany(limit)
        else:
            rows = cursor.fetchall()
    return [
        {
            "id": r[0],
            "amount": r[1],
            "type": r[2],
            "reason": r[3],
            "created_at": r[4],
            "account_name": r[5],
            "category_name": r[6],
            "category_type": r[7],
        }
        for r in rows
    ]

def fetch_latest_transaction(telegram_id: int) -> Dict:
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(get_query.get_latest_transaction_query, (telegram_id,))
        row = cursor.fetchone()
        print(f"Latest transaction row: {row}")

        cursor.execute(get_query.get_category_name, (row[4],))
        cat_row = cursor.fetchone()
        print(row)
    if row:
        return {"id": row[0], "amount": row[1], "type": row[2], "reason": row[3], "created_at": row[5], "status": row[6],"category_name":cat_row[0]}
    return {}

def fetch_total_spending_per_category(telegram_id: int) -> List[Dict]:
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(get_query.get_total_spending_per_category_query, (telegram_id,))
        rows = cursor.fetchall()
    return [{"category_name": r[0], "category_type": r[1], "total_amount": r[2]} for r in rows]

def fetch_monthly_spending_summary(telegram_id: int) -> List[Dict]:
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(get_query.get_monthly_spending_summary_query, (telegram_id,))
        rows = cursor.fetchall()
    return [{"month": r[0], "total_spent": r[1], "total_earned": r[2]} for r in rows]

def mark_transaction_undone(txn_id: int):
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE transactions SET status = 'undone' WHERE id = %s", (txn_id,)
        )
        conn.commit()

def generate_and_store_otp(telegram_id, account_id, validity_minutes=5):
    otp = random.randint(100000, 999999)  # 6-digit OTP
    expires_at = datetime.now() + timedelta(minutes=validity_minutes)
    
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO otp_codes (telegram_id, account_id, otp, expires_at) VALUES (%s,%s, %s, %s)",
            (telegram_id,account_id, otp, expires_at)
        )
        conn.commit()
    return otp

def verify_otp(entered_otp):
    print(f"Verifying OTP: {entered_otp}")
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT telegram_id,account_id, expires_at FROM otp_codes WHERE otp = %s",
            (entered_otp,)
        )
        row = cursor.fetchone()
        print(f"OTP verification row: {row}")
        if row:
            telegram_id, account_id, expires_at= row
            if datetime.now() > expires_at:
                # OTP expired
                print("OTP has expired.")
                cursor.execute("DELETE FROM otp_codes WHERE otp = %s", (entered_otp,))
                conn.commit()
                return None
            
            # OTP is valid; remove it after use
            cursor.execute("DELETE FROM otp_codes WHERE otp = %s", (entered_otp,))
            conn.commit()
            print(telegram_id,account_id)
            return (telegram_id,account_id)
    return None

def search_transactions(
    telegram_id: str,
    text: str | None = None,
    category_id: int | None = None,
    created_at: str | None = None,
    tx_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
):
    base_query = """
    SELECT
        t.id, t.amount, t.type, t.reason, t.created_at,
        a.name AS account_name,
        c.name AS category_name
    FROM transactions t
    JOIN accounts a ON t.account_id = a.id
    LEFT JOIN categories c ON t.category_id = c.id
    WHERE a.telegram_id = %s
    """
    
    params = [telegram_id]

    if tx_type:
        base_query += " AND t.type = %s"
        params.append(tx_type)

    if category_id:
        base_query += " AND t.category_id = %s"
        params.append(str(category_id))

    if created_at:
        base_query += " AND DATE(t.created_at) = %s"
        params.append(created_at)

    if text:
        base_query += " AND t.reason ILIKE %s"
        params.append(f"%{text}%")

    base_query += " ORDER BY t.created_at DESC LIMIT %s OFFSET %s"
    params.extend([ str(limit), str(offset) ])

    with get_conn() as conn, conn.cursor() as cursor:
        cursor.execute(base_query, params)
        return cursor.fetchall()
def count_total_transactions():
    with get_conn() as conn, conn.cursor() as cursor:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM transactions")
        total = cursor.fetchone()["total"]
        return total
