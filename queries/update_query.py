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
