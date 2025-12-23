from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
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
            # keyboard = [
            #         [InlineKeyboardButton("credit", callback_data="credit")],
            #         [InlineKeyboardButton("debit", callback_data="debit")],
            #         [InlineKeyboardButton("report", callback_data="report")],
            # ]
            # reply_markup = InlineKeyboardMarkup(keyboard)


            # await update.message.reply_text("Choose", reply_markup=reply_markup)

            AppContext().first_name = name
            AppContext().userName = user.username
            AppContext().telegram_id = telegram_id

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
async def credit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("credit command invoked")
    if update.effective_chat is not None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Credit command received."
        )
async def debit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("debit command invoked")
    if update.effective_chat is not None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Debit command received."
        )
async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("report command invoked")
    if update.effective_chat is not None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Report command received."
        )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    """Parses the CallbackQuery and updates the message text."""

    query = update.callback_query

    if query is None:
        print("non-command")
        return

    await query.answer()
    await query.edit_message_text(text=f"Selected option: {query.data}")
