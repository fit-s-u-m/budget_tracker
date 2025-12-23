from telegram import Update,ReplyKeyboardMarkup,ReplyKeyboardRemove
from telegram.ext import ContextTypes,ConversationHandler
from bots.context import AppContext
from core.database import fetch_accounts_by_telegram_id,insert_transaction,fetch_current_balance
from utils.category import CATEGORY_KEYWORDS, get_category_from_reason

TYPE, AMOUNT, REASON = range(3)
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("text message received")
    if update.effective_chat is not None:
        if update.message and update.message.from_user:
            message = update.message
            user = update.message.from_user
            telegram_id = user.id
            name = user.first_name
            account = fetch_accounts_by_telegram_id(telegram_id)
            account_id = account[0]['id'] if account else None

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="hi"
            )

async def handle_transaction_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return

    reply_keyboard = [["Debit", "Credit"]]

    await update.message.reply_text(
        "Choose transaction type:",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            resize_keyboard=True
        ),
    )
    return TYPE

async def handle_transaction_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None or update.message.text is None or context.user_data is None:
        return

    context.user_data["type"] = update.message.text.lower()

    await update.message.reply_text(
            "Enter the amount:",
            reply_markup=ReplyKeyboardRemove(),
        )
    return AMOUNT

async def handle_transaction_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.message.text is None or context.user_data is None:
        print("No message or user data, aborting transaction.")
        return ConversationHandler.END

    try:
        amount = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Please enter a valid number.")
        return AMOUNT

    context.user_data["amount"] = amount

    categories = list(CATEGORY_KEYWORDS.keys()) + ["other"]
    reply_keyboard = [[c] for c in categories]

    await update.message.reply_text(
        "Enter the reason or choose a category:",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            resize_keyboard=True
        ),
    )
    return REASON

async def handle_transaction_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data or not update.message:
         return ConversationHandler.END
    appContext = AppContext()
    account_id = appContext.account_id
    telegram_id = appContext.telegram_id

    if account_id is None or telegram_id is None:
        print("No account found, aborting transaction.run  /start command to register.")
        return ConversationHandler.END

    context.user_data["reason"] = update.message.text
    user_data = context.user_data
    category_name = get_category_from_reason(user_data["reason"])
    try:
        amount = int(user_data["amount"])
    except ValueError:
        print("Invalid amount, aborting transaction.")
        return ConversationHandler.END

    insert_transaction(account_id, category_name, amount, user_data["type"], user_data["reason"])

    balance = fetch_current_balance(account_id, telegram_id)

    await update.message.reply_text(
        f"✅ Transaction saved successfully! \n your balance is: {balance:.2f} birr",
        reply_markup=ReplyKeyboardRemove()
    )
    print("conversation data:", user_data)
    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""

    if update.message is None:
        return 0
    user = update.message.from_user

    await update.message.reply_text(
        "Bye", reply_markup=ReplyKeyboardRemove()
    )


    return ConversationHandler.END
