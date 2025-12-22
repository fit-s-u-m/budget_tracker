from telegram import Update
from telegram.ext import ContextTypes
from bots.context import AppContext
from core.database import fetch_accounts_by_telegram_id

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

