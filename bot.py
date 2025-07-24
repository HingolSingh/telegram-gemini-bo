#!/usr/bin/env python3
"""
Main Telegram bot application for conversational AI interactions.
"""
import logging
import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from handlers import start_command, help_command, handle_message, error_handler
from config import TELEGRAM_BOT_TOKEN, LOG_LEVEL

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO)
)
logger = logging.getLogger(__name__)


def main():
    """Start the bot."""
    # Validate required environment variables
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is required")
        return
    
    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Register message handler for all text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    logger.info("Starting Telegram bot...")
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=["message"])


if __name__ == '__main__':
    main()
