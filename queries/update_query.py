from psycopg import sql
add_balance_query = sql.SQL('''
   UPDATE accounts
        SET balance = balance + %s
        WHERE id = %s
''')
subtract_balance_query = sql.SQL('''
    UPDATE accounts
        SET balance = balance - %s
        WHERE id = %s
''')

undo_transaction_query = sql.SQL("""
    WITH original AS (
        SELECT id, account_id, category_id, amount, type
        FROM transactions
        WHERE id = %s AND status = 'active'
    ),
    counter AS (
        INSERT INTO transactions (
            account_id,
            category_id,
            amount,
            type,
            status,
            reason
        )
        SELECT
            account_id,
            category_id,
            amount,
            CASE
                WHEN type = 'debit'  THEN 'credit'
                ELSE 'debit'
            END,
            'undo',
            %s
        FROM original
        RETURNING id, account_id, amount, type
    ),
    updated AS (
        UPDATE accounts
           SET balance = balance +
               CASE
                   WHEN counter.type = 'credit' THEN counter.amount
                   ELSE -counter.amount
               END
          FROM counter
         WHERE accounts.id = counter.account_id
         RETURNING counter.id
    )
    SELECT id FROM updated;
""")

update_transaction_query = sql.SQL("""
    WITH old AS (
        SELECT account_id, amount, type
        FROM transactions
        WHERE id = %s AND status = 'active'
    ),
    reversed AS (
        UPDATE accounts
           SET balance = balance +
               CASE
                   WHEN old.type = 'debit'  THEN old.amount
                   ELSE -old.amount
               END
          FROM old
         WHERE accounts.id = old.account_id
         RETURNING accounts.id
    ),
    updated AS (
        UPDATE transactions
           SET amount = %s,
               type = %s,
               category_id = %s,
               reason = %s
         WHERE id = %s
         RETURNING account_id, amount, type
    )
    UPDATE accounts
       SET balance = balance +
           CASE
               WHEN updated.type = 'credit' THEN updated.amount
               ELSE -updated.amount
           END
      FROM updated
     WHERE accounts.id = updated.account_id;
""")
