from psycopg import sql

get_accounts_by_telegram_id_query = sql.SQL('''
    SELECT id, name, balance, created_at
    FROM accounts
    WHERE telegram_id = %s;
''')

get_category_name = sql.SQL('''
    SELECT name
    FROM categories
    WHERE id = %s;
''')

get_account_transactions_query = sql.SQL('''
    SELECT 
        t.id,
        t.amount,
        t.type,
        t.reason,
        t.created_at,
        a.name AS account_name,
        c.name AS category_name,
        c.type AS category_type
    FROM transactions t
    JOIN accounts a ON t.account_id = a.id
    LEFT JOIN categories c ON t.category_id = c.id
    WHERE a.telegram_id = %s
    ORDER BY t.created_at DESC;
''')

get_current_balance_query = sql.SQL('''
    SELECT balance
    FROM accounts
    WHERE id = %s AND telegram_id = %s;
''')

get_all_accounts_with_balance_query = sql.SQL('''
    SELECT 
        a.id,
        a.name,
        COALESCE(SUM(CASE WHEN t.type='credit' THEN t.amount ELSE -t.amount END), 0) AS balance
    FROM accounts a
    LEFT JOIN transactions t ON t.account_id = a.id
    WHERE a.telegram_id = %s
    GROUP BY a.id, a.name;
''')

# Total spending per category for a user
get_total_spending_per_category_query = sql.SQL('''
    SELECT 
        c.name AS category_name,
        c.type AS category_type,
        SUM(t.amount) AS total_amount
    FROM transactions t
    JOIN accounts a ON t.account_id = a.id
    JOIN categories c ON t.category_id = c.id
    WHERE a.telegram_id = %s 
        AND t.type='debit'
        AND t.status='active'
    GROUP BY c.id, c.name, c.type
    ORDER BY total_amount DESC;
''')

# Monthly spending summary
get_monthly_spending_summary_query = sql.SQL('''
    SELECT 
        TO_CHAR(t.created_at, 'YYYY-MM') AS month,
        SUM(CASE WHEN t.type='debit' THEN t.amount ELSE 0 END) AS total_spent,
        SUM(CASE WHEN t.type='credit' THEN t.amount ELSE 0 END) AS total_earned
    FROM transactions t
    JOIN accounts a ON t.account_id = a.id
    WHERE a.telegram_id = %s AND t.status='active'
    GROUP BY month
    ORDER BY month DESC;
''')

get_latest_transaction_query = sql.SQL('''
    SELECT t.id, t.amount, t.type, t.reason, t.category_id, t.created_at, t.status
    FROM transactions t
    JOIN accounts a ON t.account_id = a.id
    WHERE a.telegram_id = %s
    ORDER BY t.created_at DESC
    LIMIT 1;
''')
# search transactions
search_transactions_query = sql.SQL('''
    SELECT
        t.id,
        t.amount,
        t.type,
        t.reason,
        t.created_at,
        a.name  AS account_name,
        c.name  AS category_name
    FROM transactions t
    JOIN accounts a ON t.account_id = a.id
    LEFT JOIN categories c ON t.category_id = c.id
    WHERE a.telegram_id = %s
        AND (%s IS NULL OR t.type = %s)
        AND (%s IS NULL OR t.category_id = %s)
        AND (%s IS NULL OR t.created_at >= %s)
    ORDER BY t.created_at DESC NULLS LAST
    LIMIT %s OFFSET %s;
''')
