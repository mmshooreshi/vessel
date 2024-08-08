from utils.telegram_bot import setup_bot
from utils.logging import setup_logging

# Global variable to store the bot application
application = None

def main():
    global application
    setup_logging()
    application = setup_bot()

if __name__ == "__main__":
    main()
