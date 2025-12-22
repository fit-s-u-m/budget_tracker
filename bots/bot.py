from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from bots.handlers.commands import start, help_command
from bots.handlers.messages import handle_text


def init_bot(token: str) -> Application:
    app = Application.builder().token(token).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # Message handlers (non-command text)
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
    )

    app.run_polling()
    return app
