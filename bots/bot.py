from telegram import BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from bots.handlers.commands import start, help_command,credit_command,debit_command,report_command,button
from bots.handlers.messages import handle_text
def init_bot(token: str) -> Application:


    app = Application.builder().token(token).build()


    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("credit", credit_command))
    app.add_handler(CommandHandler("debit", debit_command))
    app.add_handler(CommandHandler("report", report_command))
    # app.add_handler(CallbackQueryHandler(button))

    # Message handlers (non-command text)
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
    )

    app.run_polling()

    return app
