insert_user_query = '''
    INSERT OR IGNORE INTO users (telegram_id, name)
    VALUES (?, ?)
    RETURNING id, telegram_id, name;

'''
insert_account_query ='''
    INSERT OR IGNORE INTO accounts (telegram_id, name)
    VALUES (?, ?)
    RETURNING id, telegram_id, name;
'''
insert_category_query ='''
    INSERT OR IGNORE INTO categories (name, type)
    VALUES (?, ?)
'''
insert_transaction_query ='''
    INSERT INTO transactions (account_id, category_id, amount, type, reason)
    VALUES (?, ?, ?, ?, ?)
'''
