# 💰 Budget Tracker

Budget Tracker is a personal finance tracking application that works in two ways:

- 🤖 Telegram Bot – manage your expenses directly from Telegram
- 🌐 REST API (FastAPI) – power a web or mobile frontend with analytics and reports

The system stores transactions, automatically categorizes them, tracks account balances, and generates financial reports.

The database is powered by SQLite, and the application is built using Python with the FastAPI framework.

## 🚀 Start Here
### 📌 How the System Works (Telegram Flow)

1. Start the bot using the /start command
  - Registers the user
  - Creates an account automatically

2. Check your balance using:

```sh
/balance
```

3. Credit money (add income):

```sh
/credit <amount> <reason>
```

  - Automatically detects and assigns a category

4. Debit money (record an expense):

```sh
/debit <amount> <reason>
```


  - Automatically detects and assigns a category

5. Undo the last transaction:

```sh
/undo
```


  - Reverts the previous transaction

  - Restores the balance safely

6. View recent transactions:
```sh
/transactions [limit]
```

7. Generate reports:
```sh
/report
```

---

## 🌐 API + Frontend

All Telegram bot actions are backed by the FastAPI REST API.

This allows you to:

- Build a web or mobile frontend

- Display analytics and reports

- Reuse the same business logic for multiple clients

> ⚠️ Frontend implementation is not included in this repository.


