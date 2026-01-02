from psycopg import sql

# ----------------------------
# Add balance to a user
# ----------------------------
add_balance_query = sql.SQL('''
   UPDATE users
   SET balance = balance + %s
   WHERE telegram_id = %s
''')

# ----------------------------
# Subtract balance from a user
# ----------------------------
subtract_balance_query = sql.SQL('''
    UPDATE users
    SET balance = balance - %s
    WHERE telegram_id = %s
''')

# ----------------------------
# Undo a transaction
# ----------------------------
undo_transaction_query = sql.SQL("""
    WITH original AS (
        SELECT id, telgram_id, category, amount, type
        FROM transactions
        WHERE id = %s AND status = 'active'
    ),
    counter AS (
        INSERT INTO transactions (
            id,
            telegram_id,
            category,
            amount,
            type,
            status,
            reason
        )
        SELECT
            gen_random_uuid(),
            telegram_id,
            category,
            amount,
            CASE
                WHEN type = 'debit'  THEN 'credit'
                ELSE 'debit'
            END,
            'undo',
            reason || ' undo'  -- append 'undo' to original reason
        FROM original
        RETURNING id, telegram_id, amount, type
    ),
    updated AS (
        UPDATE users
           SET balance = balance +
               CASE
                   WHEN counter.type = 'credit' THEN counter.amount
                   ELSE -counter.amount
               END
          FROM counter
         WHERE users.telegram_id = counter.telegram_id
         RETURNING counter.id
    )
    SELECT id FROM updated;
""")

# ----------------------------
# Update a transaction (adjust user balance)
# ----------------------------
update_transaction_query = sql.SQL("""
    WITH old AS (
        SELECT telegram_id, amount, type
        FROM transactions
        WHERE id = %s AND status = 'active'
    ),
    reversed AS (
        UPDATE users
           SET balance = balance +
               CASE
                   WHEN old.type = 'debit'  THEN old.amount
                   ELSE -old.amount
               END
          FROM old
         WHERE users.telegram_id = old.telegram_id
         RETURNING users.id
    ),
    updated AS (
        UPDATE transactions
           SET amount = %s,
               type = %s,
               category = %s,
               reason = %s
         WHERE id = %s
         RETURNING telegram_id, amount, type
    )
    UPDATE users
       SET balance = balance +
           CASE
               WHEN updated.type = 'credit' THEN updated.amount
               ELSE -updated.amount
           END
      FROM updated
     WHERE users.telegram_id = updated.telegram_id;
""")
