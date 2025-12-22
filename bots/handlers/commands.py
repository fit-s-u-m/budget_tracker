from telegram import Update
from telegram.ext import ContextTypes
from core.database import insert_user,create_account
from bots.context import AppContext

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("start command invoked")
    if update.effective_chat is not None:
        if update.message and update.message.from_user:
            user = update.message.from_user
            telegram_id = user.id
            name = user.first_name

            insert_user(telegram_id, name)
            create_account(telegram_id, name)

            # AppContext().first_name = name
            # AppContext().userName = user.username
            # AppContext().telegram_id = telegram_id

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Successfully registered! Welcome to the Budget Bot."
            )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("help command invoked")
    if update.effective_chat is not None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="To register run: \n/start"
        )
