from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from core.database import insert_transaction, insert_user,create_account,fetch_current_balance,fetch_monthly_spending_summary,fetch_latest_transaction,fetch_total_spending_per_category
from bots.context import AppContext
from queries import insert_query

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

async def credit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    print(f"credit command invoked with {args}")
    if update.message is not None:
        if not args or len(args) < 2:
            print("not enough args")
            await update.message.reply_text(
                "Usage: /credit <amount> <description>"
            )
            return
        if AppContext().account_id is None:
            print("account_id is None")
            await update.message.reply_text(
                "Please register first using /start command."
            )
            return
        account_id = AppContext().account_id
        if account_id is None:
            print("account_id is still None")
            return
        category_name = "general"
        amount = args[0] if args[0].isdigit() else None 
        reason = " ".join(args[1:])
        typeOf = "credit"
        if amount is None:
            return

        print(f"Adding transaction to account_id: {account_id}, category_name: {category_name}, amount: {amount}, type: {typeOf}, reason: {reason}")
        insert_transaction(account_id,category_name,amount,"credit",reason )


    if update.effective_chat is not None:

        account_id = AppContext().account_id
        telegram_id = AppContext().telegram_id

        if account_id is None and telegram_id is None:
            print("account_id is still None")
            return
        balance = fetch_current_balance(account_id, telegram_id)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Transaction credited successfully."
        )
        print(f"check_balance command invoked, balance: {balance}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Your current balance is: {balance:.2f} birr"
        )

async def debit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    print(f"debit command invoked with {args}")
    if update.message is not None:
        if not args or len(args) < 2:
            print("not enough args")
            await update.message.reply_text(
                "Usage: /debit <amount> <description>"
            )
            return
        if AppContext().account_id is None:
            print("account_id is None")
            await update.message.reply_text(
                "Please register first using /start command."
            )
            return
        account_id = AppContext().account_id
        if account_id is None:
            print("account_id is still None")
            return
        category_name = "general"
        amount = args[0] if args[0].isdigit() else None
        reason = " ".join(args[1:])
        typeOf = "debit"


        print(f"Adding transaction to account_id: {account_id}, category_name: {category_name}, amount: {amount}, type: {typeOf}, reason: {reason}")
        insert_transaction(account_id,category_name,amount,typeOf,reason )



    if update.effective_chat is not None:
        account_id = AppContext().account_id
        telegram_id = AppContext().telegram_id

        if account_id is None or telegram_id is None:
            print("account_id is still None")
            return
        balance = fetch_current_balance(account_id, telegram_id)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Transaction credited successfully."
        )
        print(f"check_balance command invoked, balance: {balance}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Your current balance is: {balance:.2f} birr"
        )

async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = AppContext().telegram_id  # make sure telegram_id is set in your context
    if telegram_id is None:
        print("telegram_id is None")
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

# useful
# keyboard = [
#         [InlineKeyboardButton("credit", callback_data="credit")],
#         [InlineKeyboardButton("debit", callback_data="debit")],
#         [InlineKeyboardButton("report", callback_data="report")],
# ]
# reply_markup = InlineKeyboardMarkup(keyboard)
#
#
# await update.message.reply_text("Choose", reply_markup=reply_markup)
