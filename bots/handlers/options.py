from telegram.ext import MessageHandler, filters,ContextTypes
from telegram import Update

async def attendance(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat is not None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="📊 Attendance report"
        )

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat is not None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="👤 Your profile"
        )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat is not None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Cancelled",
            reply_markup=ReplyKeyboardRemove(),
        )

