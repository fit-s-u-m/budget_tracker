from psycopg import sql

create_user_table = sql.SQL('''
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''')

create_account_table = sql.SQL('''
CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    balance INTEGER NOT NULL CHECK (amount >= 0) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (telegram_id) REFERENCES users(telegram_id)
);
''')

create_category_table = sql.SQL('''
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    type TEXT CHECK(type IN ('debit', 'credit')) NOT NULL
);
''')

create_transaction_table = sql.SQL('''
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL,
    category_id INTEGER,
    amount INTEGER NOT NULL CHECK (amount >= 0),
    type TEXT CHECK(type IN ('debit', 'credit')) NOT NULL,
    status TEXT DEFAULT 'active',
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
''')

create_index = sql.SQL('''
CREATE INDEX IF NOT EXISTS idx_accounts_telegram_id
ON accounts(telegram_id);
''')

create_otp_codes = sql.SQL('''
CREATE TABLE IF NOT EXISTS otp_codes (
    telegram_id BIGINT NOT NULL,
    account_id  INTEGER NOT NULL,
    otp INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);
''')
