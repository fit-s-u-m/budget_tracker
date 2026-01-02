from psycopg import sql

# Get user by telegram_id (was get_accounts_by_telegram_id_query)
get_user_by_telegram_id_query = sql.SQL('''
    SELECT id, name, balance, created_at
    FROM users
    WHERE telegram_id = %s;
''')

# Get category name by id
get_category_name_query = sql.SQL('''
    SELECT name
    FROM categories
    WHERE id = %s;
''')

# Get all transactions for a user
get_user_transactions_query = sql.SQL('''
    SELECT 
        t.id,
        t.amount,
        t.type,
        t.reason,
        t.created_at,
        t.category AS category_name,
        t.status
    FROM transactions t
    LEFT JOIN categories c ON t.category = c.name
    WHERE t.telegram_id = %s
    ORDER BY t.created_at DESC NULLS LAST
''')

# Get current balance for a user
get_current_balance_query = sql.SQL('''
    SELECT balance
    FROM users
    WHERE id = %s AND telegram_id = %s;
''')

# Total spending per category for a user
get_total_spending_per_category_query = sql.SQL('''
    SELECT 
        t.category AS category_name,
        c.type AS category_type,
        SUM(t.amount) AS total_amount
    FROM transactions t
    LEFT JOIN categories c ON t.category = c.name
    WHERE t.telegram_id = %s
        AND t.type='debit'
        AND t.status='active'
    GROUP BY t.category, c.type
    ORDER BY total_amount DESC;
''')

# Monthly spending summary
get_monthly_spending_summary_query = sql.SQL('''
    SELECT 
        TO_CHAR(t.created_at, 'YYYY-MM') AS month,
        SUM(CASE WHEN t.type='debit' THEN t.amount ELSE 0 END) AS total_spent,
        SUM(CASE WHEN t.type='credit' THEN t.amount ELSE 0 END) AS total_earned
    FROM transactions t
    WHERE t.telegram_id = %s AND t.status='active'
    GROUP BY month
    ORDER BY month DESC;
''')

# Get latest transaction for a user
get_latest_transaction_query = sql.SQL('''
    SELECT t.id, t.amount, t.type, t.reason, t.category, t.created_at, t.status
    FROM transactions t
    WHERE t.telegram_id = %s
    ORDER BY t.created_at DESC
    LIMIT 1;
''')

# Search transactions
search_transactions_query = sql.SQL('''
    SELECT
        t.id,
        t.amount,
        t.type,
        t.reason,
        t.created_at,
        t.category AS category_name,
        t.status
    FROM transactions t
    LEFT JOIN categories c ON t.category = c.name
    WHERE t.telegram_id = %s
        AND (%s IS NULL OR t.type = %s)
        AND (%s IS NULL OR t.category = %s)
        AND (%s IS NULL OR t.created_at >= %s)
    ORDER BY t.created_at DESC NULLS LAST
    LIMIT %s OFFSET %s;
''')
