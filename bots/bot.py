from telegram import BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from bots.handlers.commands import check_balance_command, start, help_command,transaction_command,report_command,button,transactions_command, undo_command
from bots.handlers.messages import handle_text
async def set_commands(app):
    print("set command is called")

    #
    # return lambda async():(
    await app.bot.set_my_commands([
        BotCommand("start", "Register /start using the bot"),
        BotCommand("balance", "Check balance /balance"),
        BotCommand("credit", "Credit an amount: /credit <amount> <description>"),
        BotCommand("debit", "Debit an amount: /debit <amount> <type> <description>"),
        BotCommand("report", "Get report: /report"),
        BotCommand("transactions", "Get transactions: /tranactions <limit>"),
        BotCommand("help", "Show help information"),
        BotCommand("undo_transaction", "undo previous transaction"),
    ])

def init_bot(token: str) -> Application:

    app = Application.builder().token(token).build()
    app.post_init = set_commands


    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", check_balance_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("credit", lambda u, c: transaction_command(u, c, "credit")))
    app.add_handler(CommandHandler("debit", lambda u, c: transaction_command(u, c, "debit")))
    app.add_handler(CommandHandler("report", report_command))
    app.add_handler(CommandHandler("transactions", transactions_command))
    app.add_handler(CommandHandler("undo_transaction", undo_command))
    # app.add_handler(CallbackQueryHandler(button))

    # Message handlers (non-command text)
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
    )

    app.run_polling()

    return app
