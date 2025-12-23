from telegram import Update
from telegram.ext import ContextTypes

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("text message received")
    if update.effective_chat is not None:
        if update.message and update.message.from_user:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Please use /help to see available commands."
            )
