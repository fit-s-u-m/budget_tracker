from psycopg import sql

create_user_table = sql.SQL('''
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    balance INTEGER NOT NULL DEFAULT 0 CHECK (balance >= 0)
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
    id UUID PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    category TEXT,
    amount INTEGER NOT NULL CHECK (amount >= 0),
    type TEXT CHECK (type IN ('debit', 'credit')) NOT NULL,
    status TEXT DEFAULT 'active',
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (telegram_id) REFERENCES users(telegram_id) ON DELETE CASCADE,
    FOREIGN KEY (category) REFERENCES categories(name)
);
''')


create_index = sql.SQL('''

    CREATE INDEX IF NOT EXISTS idx_users_telegram_id
    ON users (telegram_id);

    CREATE INDEX IF NOT EXISTS idx_transactions_telegram_id
    ON transactions (telegram_id);

    CREATE INDEX IF NOT EXISTS idx_transactions_created_at
    ON transactions (created_at DESC NULLS LAST);

    CREATE INDEX IF NOT EXISTS idx_transactions_type
    ON transactions (type);

    CREATE INDEX IF NOT EXISTS idx_transactions_category
    ON transactions (category);

    CREATE INDEX IF NOT EXISTS idx_transactions_updated_at
    ON transactions (updated_at);
''')


create_otp_codes = sql.SQL('''
CREATE TABLE IF NOT EXISTS otp_codes (
    telegram_id BIGINT NOT NULL,
    otp INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);
''')
create_auto_update = sql.SQL('''
    DROP TRIGGER IF EXISTS trg_transactions_updated_at ON transactions;
    CREATE OR REPLACE FUNCTION set_updated_at()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    CREATE TRIGGER trg_transactions_updated_at
    BEFORE UPDATE ON transactions
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at();
''')
