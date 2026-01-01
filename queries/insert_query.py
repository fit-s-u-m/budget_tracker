from psycopg import sql
import uuid

# ----------------------------
# Insert a user, ignore conflict on telegram_id
# ----------------------------
insert_user_query = sql.SQL('''
    INSERT INTO users (telegram_id, name)
    VALUES (%s, %s)
    ON CONFLICT (telegram_id) DO NOTHING
    RETURNING id, telegram_id, name, balance;
''')

# ----------------------------
# Insert category, ignore conflict on name
# ----------------------------
insert_category_query = sql.SQL('''
    INSERT INTO categories (name, type)
    VALUES (%s, %s)
    ON CONFLICT (name) DO NOTHING
    RETURNING id, name, type;
''')

# ----------------------------
# Insert transaction
# ----------------------------
insert_transaction_query = sql.SQL('''
    INSERT INTO transactions (
        id,
        telegram_id,
        category,
        amount,
        type,
        reason,
        status
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    RETURNING id, telegram_id, category, amount, type, reason, status, created_at, updated_at;
''')
