#!/usr/bin/env python3
"""
Advanced Multi-AI Telegram Bot with comprehensive features.
"""
import logging
import os
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.ext import CallbackQueryHandler
from config import TELEGRAM_BOT_TOKEN, LOG_LEVEL
from database import init_database, get_session
from handlers import advanced_handlers
from analytics import AnalyticsManager

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def main():
    """Start the advanced bot."""
    # Validate required environment variables
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is required")
        return
    
    # Initialize database
    await init_database()
    
    # Initialize analytics
    analytics = AnalyticsManager()
    
    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Register all handlers
    handlers = advanced_handlers.AdvancedHandlers(analytics)
    
    # Command handlers
    application.add_handler(CommandHandler("start", handlers.start_command))
    application.add_handler(CommandHandler("help", handlers.help_command))
    application.add_handler(CommandHandler("profile", handlers.profile_command))
    application.add_handler(CommandHandler("settings", handlers.settings_command))
    application.add_handler(CommandHandler("ai", handlers.switch_ai_command))
    application.add_handler(CommandHandler("stats", handlers.stats_command))
    application.add_handler(CommandHandler("learn", handlers.learn_command))
    application.add_handler(CommandHandler("generate", handlers.generate_image_command))
    application.add_handler(CommandHandler("memory", handlers.memory_command))
    application.add_handler(CommandHandler("export", handlers.export_data_command))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_text_message))
    application.add_handler(MessageHandler(filters.VOICE, handlers.handle_voice_message))
    application.add_handler(MessageHandler(filters.AUDIO, handlers.handle_audio_message))
    application.add_handler(MessageHandler(filters.PHOTO, handlers.handle_photo_message))
    application.add_handler(MessageHandler(filters.Document.ALL, handlers.handle_document_message))
    
    # Callback query handler for inline keyboards
    application.add_handler(CallbackQueryHandler(handlers.handle_callback_query))
    
    # Error handler
    application.add_error_handler(handlers.error_handler)
    
    logger.info("Starting Advanced Telegram Bot...")
    
    # Run the bot
    await application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == '__main__':
    asyncio.run(main())