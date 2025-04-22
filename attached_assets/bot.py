import os
import logging
import telebot
from telebot import types

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def run_bot():
    """Initialize and run the Telegram bot."""
    # Get the bot token from environment variables
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    
    if not token:
        logger.error("No TELEGRAM_BOT_TOKEN found in environment variables!")
        return
    
    # Create the bot instance
    bot = telebot.TeleBot(token)
    
    # Import handlers here to avoid circular imports
    from handlers import register_handlers
    
    # Register all handlers
    register_handlers(bot)
    
    # Run the bot
    logger.info("Starting bot...")
    bot.infinity_polling()
