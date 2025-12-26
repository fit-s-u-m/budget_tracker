from psycopg import sql

# Insert a user, ignore conflict on telegram_id
insert_user_query = sql.SQL('''
    INSERT INTO users (telegram_id, name)
    VALUES (%s, %s)
    ON CONFLICT (telegram_id) DO NOTHING
    RETURNING id, telegram_id, name;
''')

# Insert an account, ignore conflict on telegram_id
insert_account_query = sql.SQL('''
    INSERT INTO accounts (telegram_id, name)
    VALUES (%s, %s)
    ON CONFLICT (telegram_id) DO NOTHING
    RETURNING id, telegram_id, name;
''')

# Insert category, ignore conflict on name (or name+type depending on your schema)
insert_category_query = sql.SQL('''
    INSERT INTO categories (name, type)
    VALUES (%s, %s)
    ON CONFLICT (name) DO NOTHING
    RETURNING id, name, type;
''')

# Insert transaction
insert_transaction_query = sql.SQL('''
    INSERT INTO transactions (account_id, category_id, amount, type, reason, created_at)
    VALUES (%s, %s, %s, %s, %s, %s)
    RETURNING id, account_id, category_id, amount, type, reason, created_at;
''')
