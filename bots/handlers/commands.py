from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from utils.category import get_category_from_reason 
from core.database import(
    insert_transaction,
    insert_user,
    create_account,
    fetch_current_balance,
    fetch_monthly_spending_summary,
    fetch_latest_transaction,
    fetch_total_spending_per_category,
    mark_transaction_undone,
    fetch_transactions_for_user,
)
from bots.context import AppContext

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("start command invoked")
    if update.effective_chat is not None:
        if update.message and update.message.from_user:
            user = update.message.from_user
            telegram_id = user.id
            name = user.first_name

            insert_user(telegram_id, name)
            account_id = create_account(telegram_id, name)

            AppContext().first_name = name
            AppContext().userName = user.username
            AppContext().telegram_id = telegram_id
            AppContext().account_id = account_id

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Successfully registered! Welcome to the Budget Bot."
            )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("help command invoked")
    if update.effective_chat is not None:
        await context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = """
📘 *Available Commands*

/start  
Register and start using the bot

/credit `<amount>` `<description>`  
Credit an amount

/debit `<amount>` `<type>` `<description>`  
Debit an amount

/report `<daily | weekly | monthly>`  
Get expense report

/help  
Show this help message
            """,
            parse_mode="Markdown"
    )
async def check_balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    account_id = AppContext().account_id
    telegram_id = AppContext().telegram_id
    if update.effective_chat is not None:
        if account_id is None or telegram_id is None:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Please register first using /start command."
            )
            return
        balance = fetch_current_balance(account_id, telegram_id)
        print(f"check_balance command invoked, balance: {balance}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Your current balance is: {balance:.2f} birr"
        )

async def transaction_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    typeOf: str  # "credit" or "debit"
):
    args = context.args
    appContext = AppContext()
    print(f"{typeOf} command invoked with {args}")

    if update.message is None:
        return

    if not args or len(args) < 2:
        await update.message.reply_text(f"Usage: /{typeOf} <amount> <description>")
        return

    account_id = appContext.account_id
    if account_id is None:
        await update.message.reply_text("Please register first using /start command.")
        return

    # Parse amount
    try:
        amount = int(args[0])
    except ValueError:
        await update.message.reply_text("Amount must be a number.")
        return

    reason = " ".join(args[1:])
    category_name = get_category_from_reason(reason)

    # Insert transaction
    insert_transaction(account_id, category_name, amount, typeOf, reason)
    print(f"Transaction added: {typeOf} {amount} for account {account_id} ({reason})")

    # Send confirmation
    telegram_id = appContext.telegram_id
    if update.effective_chat and account_id and telegram_id:
        balance = fetch_current_balance(account_id, telegram_id)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"✅ Transaction {typeOf} successfully.\n💰 Current balance: {balance:.2f} birr"
        )

async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = AppContext().telegram_id  # make sure telegram_id is set in your context

    if update.message is None:
        return
    if telegram_id is None:
        await update.message.reply_text("Please register first using /start command.")
        return

    # Fetch data
    monthly_summary = fetch_monthly_spending_summary(telegram_id)
    latest_txn = fetch_latest_transaction(telegram_id)
    spending_per_category = fetch_total_spending_per_category(telegram_id)

    # Build a nice summary text
    summary_lines = ["📊 *Your Finance Report* 📊\n"]

    # Latest transaction
    if latest_txn:
        summary_lines.append("🆕 *Latest Transaction*:")
        summary_lines.append(
            f"- {latest_txn['type'].capitalize()}: {latest_txn['amount']}\n"
            f"  Reason: {latest_txn['reason']}\n"
            f"  Date: {latest_txn['created_at']}\n"
        )

    # Spending per category
    if spending_per_category:
        summary_lines.append("💰 *Total Spending per Category*:")
        for cat in spending_per_category:
            print(cat)
            summary_lines.append(
                f"- {cat['category_name']} ({cat['category_type']}): {cat['total_amount']}"
            )

    # Monthly summary
    if monthly_summary:
        summary_lines.append("\n📅 *Monthly Summary*:")
        for month in monthly_summary:
            summary_lines.append(
                f"- {month['month']}: Spent {month['total_spent']}, Earned {month['total_earned']}"
            )

    # Join all lines
    summary_text = "\n".join(summary_lines)
    print(summary_text)

    # Send message with Markdown formatting
    if update.effective_chat:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=summary_text,
            parse_mode="Markdown"
        )
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    """Parses the CallbackQuery and updates the message text."""

    query = update.callback_query

    if query is None:
        print("non-command")
        return

    await query.answer()
    await query.edit_message_text(text=f"Selected option: {query.data}")

async def transactions_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    appContext = AppContext()
    telegram_id = appContext.telegram_id
    args = context.args
    if update.message is None:
        return

    if telegram_id is None:
        await update.message.reply_text("Please register first using /start command.")
        return

    limit = None
    if  args:
        try:
            limit = int(args[0])
        except ValueError:
            await update.message.reply_text("Amount must be a number.")
            return
    if telegram_id is None:
        await update.message.reply_text("Please register first using /start command.")
        return

    summary_lines = ["📝 Your Recent Transactions"]
    transactions = fetch_transactions_for_user(telegram_id, limit=limit)
    
    for txn in transactions:

        dt = datetime.strptime(txn['created_at'], '%Y-%m-%d %H:%M:%S')
        pretty_date = dt.strftime('%A, %d %B %Y at %I:%M %p')
        summary_lines.append(
            f"------------------------------\n"
            f"{'undo' if txn.get('status') == 'undone' else ''}\n"
            f"🗓 {pretty_date}\n"
            f"💸 {txn['type'].capitalize()}: {txn['amount']} birr\n"
            f"📝 Reason: {txn['reason']}\n"
            f"🏦 Account: {txn['account_name']}, Category: {txn['category_name']}\n"
            f"------------------------------\n"
        )
    if update.effective_chat:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="\n".join(summary_lines),
            parse_mode="Markdown"
        )

async def undo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    appContext = AppContext()
    account_id = appContext.account_id
    telegram_id = appContext.telegram_id
    if update.message is None:
        return

    if account_id is None or telegram_id is None:
        await update.message.reply_text("Please register first using /start command.")
        return

    # Fetch the latest active transaction
    latest_txn = fetch_latest_transaction(telegram_id)
    if not latest_txn or latest_txn.get("status") == "undone":
        await update.message.reply_text("No transaction to undo.")
        return

    # Determine reverse type
    reverse_type = "debit" if latest_txn["type"] == "credit" else "credit"
    print(latest_txn)

    # Insert a reversing transaction
    transaction = insert_transaction(
        account_id=account_id,
        category_name=latest_txn["category_name"],
        amount=latest_txn["amount"],
        type=reverse_type,
        reason=f"Undo: {latest_txn['reason']}"
    )
    print(transaction)
    transaction_id = transaction.get("id")

    # Mark original transaction as undone (optional)
    mark_transaction_undone(latest_txn["id"])
    mark_transaction_undone(transaction_id)

    # Send confirmation
    balance = fetch_current_balance(account_id, telegram_id)
    await update.message.reply_text(
        f"✅ Last transaction has been undone.\n💰 Current balance: {balance:.2f} birr"
    )
