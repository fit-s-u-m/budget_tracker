add_balance_query = '''
   UPDATE accounts
        SET balance = balance + ?
        WHERE id = ?
'''
subtract_balance_query = '''
    UPDATE accounts
        SET balance = balance - ?
        WHERE id = ?

'''
