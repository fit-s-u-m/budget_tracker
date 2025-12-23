import sqlite3
from queries import (
    create_query, 
    insert_query,
    update_query,
    get_query,
)
from typing import List, Dict, Optional

DB_PATH = "app.db"

# Initialize the database and create tables if they do not exist
def initalize_tables():
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()

        cursor.execute(create_query.create_user_table)
        cursor.execute(create_query.create_account_table)
        cursor.execute(create_query.create_transaction_table)
        cursor.execute(create_query.create_category_table)
        cursor.execute(create_query.create_index)

        connection.commit()
        print("Tables created successfully.")

# Insert a new user into the users table
def insert_user(telegram_id, name):
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()

        cursor.execute(insert_query.insert_user_query, (telegram_id, name))
        
        cursor.execute(
            "SELECT id, telegram_id, name FROM users WHERE telegram_id = ?",
            (telegram_id,),
        )
        user_info = cursor.fetchone()

        connection.commit()
        print(f"User inserted successfully.info: {user_info}")
        return user_info

def insert_transaction(account_id: int, category_name: str, amount:int, type:str, reason:str):

    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()

        cursor.execute(insert_query.insert_category_query, (category_name, type))

        cursor.execute(
            "SELECT id FROM categories WHERE name= ?",
            (category_name,),
        )
        category_id = cursor.fetchone()
        print(f"category_id: {category_id[0]}")

        cursor.execute(insert_query.insert_transaction_query, (account_id , category_id[0] , amount, type, reason))
        if type =="debit":
            cursor.execute(update_query.subtract_balance_query, (amount, account_id))
        if type =="credit":
            cursor.execute(update_query.add_balance_query, (amount, account_id))

        transaction_id = cursor.fetchone()
        connection.commit()
        print("transaction inserted successfully.")
        return transaction_id

# Create a new category in the categories table
def create_category(name, type):
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()

        cursor.execute(insert_query.insert_category_query, (name, type))

        connection.commit()
        print(f"Category inserted successfully.{cursor.lastrowid}")
        return cursor.lastrowid

# Create a new account in the accounts table
def create_account(telegram_id, name):
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()

        cursor.execute(insert_query.insert_account_query, (telegram_id, name))
        cursor.execute(
            "SELECT id FROM accounts WHERE telegram_id = ?",
            (telegram_id,)
        )
        account = cursor.fetchone()
        account_id = account[0]


        connection.commit()
        print("Account inserted successfully.", account_id)
        return account_id
def fetch_accounts_by_telegram_id(telegram_id: int) -> List[Dict]:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(get_query.get_accounts_by_teleram_id_query, (telegram_id,))
        rows = cursor.fetchall()
    return [{"id": r[0], "name": r[1], "balance": r[2], "created_at": r[3]} for r in rows]

def fetch_all_accounts_with_balance(telegram_id: int) -> List[Dict]:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(get_query.get_all_accounts_with_balance_query, (telegram_id,))
        rows = cursor.fetchall()
    return [{"id": r[0], "name": r[1], "balance": r[2]} for r in rows]

def fetch_current_balance(account_id: int, telegram_id: int) -> int:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(get_query.get_current_balance_query, (account_id, telegram_id))
        row = cursor.fetchone()
    return row[0] if row else 0

# ---------------- TRANSACTIONS ----------------
def fetch_transactions_for_user(telegram_id: int,limit: Optional[int] = None) -> List[Dict]:
    with sqlite3.connect(DB_PATH) as conn:
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
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(get_query.get_latest_transaction_query, (telegram_id,))
        row = cursor.fetchone()
        print(f"Latest transaction row: {row}")

        cursor.execute(get_query.get_category_name, (row[4],))
        cat_row = cursor.fetchone()
    if row:
        return {"id": row[0], "amount": row[1], "type": row[2], "reason": row[3], "created_at": row[5], "category_name":cat_row[0]}
    return {}

def fetch_total_spending_per_category(telegram_id: int) -> List[Dict]:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(get_query.get_total_spending_per_category_query, (telegram_id,))
        rows = cursor.fetchall()
    return [{"category_name": r[0], "category_type": r[1], "total_amount": r[2]} for r in rows]

def fetch_monthly_spending_summary(telegram_id: int) -> List[Dict]:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(get_query.get_monthly_spending_summary_query, (telegram_id,))
        rows = cursor.fetchall()
    return [{"month": r[0], "total_spent": r[1], "total_earned": r[2]} for r in rows]

def mark_transaction_undone(txn_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE transactions SET status = 'undone' WHERE id = ?", (txn_id,)
        )
        conn.commit()
