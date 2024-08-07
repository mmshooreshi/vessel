from utils.telegram_bot import setup_bot
from utils.logging import setup_logging

def main():
    setup_logging()
    setup_bot()

if __name__ == "__main__":
    main()
