import os

from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Session
REDIS_URL = os.getenv('REDIS_URL')

# Database Configuration
MONGO_URL = os.getenv('MONGO_URL')

# Task Queue Manager
RABBITMQ_URL = os.getenv('RABBITMQ_URL')

# API Keys and Secrets
BSC_SCAN_API_KEY = os.getenv('BSC_SCAN_API_KEY')

# Bot Configuration Options
BOT_NAME = os.getenv('BOT_NAME')
ADMIN_USER_ID = os.getenv('ADMIN_USER_ID')
