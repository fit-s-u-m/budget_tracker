from bots.bot import init_bot
from dotenv import load_dotenv
from core.database import initalize_tables
import getpass
import os

load_dotenv()
if "TELEGRAM_API_KEY" not in os.environ:
    os.environ["TELEGRAM_API_KEY"] = getpass.getpass("Enter your Telegram bot token key: ")
TOKEN = os.environ["TELEGRAM_API_KEY"]
def main():
    print("Hello from budget-tracker!")
    initalize_tables()
    _ = init_bot(TOKEN)


if __name__ == "__main__":
    main()
