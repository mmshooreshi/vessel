import subprocess
import requests
from utils.config import BOT_TOKEN, CHAT_ID
from utils.logging import log_info, log_warning, log_error, log_debug, log_critical

def handle_telegram_commands():
    # Handle commands received via Telegram
    pass  # Implementation of Telegram command handler

def execute_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip() + '\n' + result.stderr.strip()

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    log_info(f"\n----\nurl: {url}   |   CHAT_ID: {CHAT_ID}   |   parse_mode: MarkdownV2\n---")
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": 'MarkdownV2'}
    requests.post(url, data=data)
