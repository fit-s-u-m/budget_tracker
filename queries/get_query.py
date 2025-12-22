get_accounts_by_teleram_id_query = '''
    SELECT id, name, balance, created_at
    FROM accounts
    WHERE telegram_id = ?;
'''
get_account_transactions_query = '''
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
    WHERE a.telegram_id = ?
    ORDER BY t.created_at DESC;
'''
get_current_balance_query = '''
    SELECT balance
    FROM accounts
    WHERE id = ? AND telegram_id = ?;
'''
get_all_accounts_with_balance_query = '''
    SELECT 
        a.id,
        a.name,
        COALESCE(SUM(CASE WHEN t.type='credit' THEN t.amount ELSE -t.amount END),0) AS balance
    FROM accounts a
    LEFT JOIN transactions t ON t.account_id = a.id
    WHERE a.telegram_id = ?
    GROUP BY a.id, a.name;
'''

#Total spending per category for a user
get_total_spending_per_category_query = '''
    SELECT 
        c.name AS category_name,
        c.type AS category_type,
        SUM(t.amount) AS total_amount
    FROM transactions t
    JOIN accounts a ON t.account_id = a.id
    JOIN categories c ON t.category_id = c.id
    WHERE a.telegram_id = ? AND t.type='debit'
    GROUP BY c.id, c.name, c.type
    ORDER BY total_amount DESC;
'''
# Monthly spending summary
get_monthly_spending_summary_query = '''
    SELECT 
        strftime('%Y-%m', t.created_at) AS month,
        SUM(CASE WHEN t.type='debit' THEN t.amount ELSE 0 END) AS total_spent,
        SUM(CASE WHEN t.type='credit' THEN t.amount ELSE 0 END) AS total_earned
    FROM transactions t
    JOIN accounts a ON t.account_id = a.id
    WHERE a.telegram_id = ?
    GROUP BY month
    ORDER BY month DESC;
'''

get_latest_transaction_query = '''
    SELECT t.id, t.amount, t.type, t.reason, t.created_at
    FROM transactions t
    JOIN accounts a ON t.account_id = a.id
    WHERE a.telegram_id = ?
    ORDER BY t.created_at DESC
    LIMIT 1;
'''
