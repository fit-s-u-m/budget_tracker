from telegram import Update,ReplyKeyboardMarkup,ReplyKeyboardRemove
from telegram.ext import ContextTypes,ConversationHandler
from bots.context import AppContext
from core.database import insert_transaction,fetch_current_balance
from utils.category import CATEGORY_KEYWORDS, get_category_from_reason
from custom_types import State

async def handle_transaction_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        print("No message or user data, aborting transaction.")
        return ConversationHandler.END

    reply_keyboard = [["Debit", "Credit"]]

    await update.message.reply_text(
        "Choose transaction type:",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            resize_keyboard=True
        ),
    )
    return State.TYPE

async def handle_transaction_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None or update.message.text is None or context.user_data is None:
        print("No message or user data, aborting transaction.")
        return ConversationHandler.END

    context.user_data["type"] = update.message.text.lower()

    await update.message.reply_text(
            "Enter the amount:",
            reply_markup=ReplyKeyboardRemove(),
        )
    return State.AMOUNT

async def handle_transaction_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.message.text is None:
        print("No message or user data, aborting transaction.")
        return ConversationHandler.END

    try:
        amount = int(update.message.text)
        app_context = AppContext()
        account_id = app_context.account_id
        telegram_id = app_context.telegram_id
        if account_id is None or telegram_id is None:
            await update.message.reply_text(f"transaction aborted.No account found. run /start command to register.")
            print("Telegram ID or Account ID is None, aborting transaction.")
            return ConversationHandler.END
        balance = fetch_current_balance(account_id, telegram_id)

        if context.user_data and  context.user_data["type"] == "debit" and amount > balance:
            reply_keyboard = [["Debit", "Credit"]]

            await update.message.reply_text(
                f"❌ Insufficient balance.\n💰 Available: {balance:.2f} birr\nChoose transaction type again:",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard,
                    one_time_keyboard=True,
                    resize_keyboard=True
                ),
            )
            return State.TYPE

    except ValueError:
        await update.message.reply_text("Please enter a valid number.")
        return State.AMOUNT

    if context.user_data is not None:
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
    return State.REASON

async def handle_transaction_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data or not update.message:
         return ConversationHandler.END
    appContext = AppContext()
    account_id = appContext.account_id
    telegram_id = appContext.telegram_id

    if account_id is None or telegram_id is None:
        print("No account found, aborting transaction.run  /start command to register.")
        await update.message.reply_text(f"transaction aborted.No account found. run /start command to register.")
        return ConversationHandler.END

    context.user_data["reason"] = update.message.text
    user_data = context.user_data
    category_name = get_category_from_reason(user_data["reason"])
    try:
        amount = int(user_data["amount"])
    except ValueError:
        print("Invalid amount, aborting transaction.")
        await update.message.reply_text(f"transaction aborted.Invalid amount.")
        return ConversationHandler.END

    await insert_transaction(account_id, category_name, amount, user_data["type"], user_data["reason"])

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
