"""
Advanced message handlers for the multi-AI Telegram bot.
"""
import logging
import asyncio
import os
import io
import tempfile
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatAction, ParseMode

from multi_ai_client import MultiAIClient
from database import (
    get_or_create_user, save_conversation, get_user_memory, 
    save_user_memory, save_conversation
)
from analytics import AnalyticsManager
from file_processor import FileProcessor
from educational_assistant import EducationalAssistant

logger = logging.getLogger(__name__)


class AdvancedHandlers:
    """Advanced handlers for comprehensive bot functionality."""
    
    def __init__(self, analytics_manager: AnalyticsManager):
        self.ai_client = MultiAIClient()
        self.analytics = analytics_manager
        self.file_processor = FileProcessor()
        self.edu_assistant = EducationalAssistant(self.ai_client)
        
        # User conversation contexts
        self.user_contexts = {}
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Enhanced start command with user registration."""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        # Get or create user in database
        db_user = await get_or_create_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        # Clear conversation context
        self.user_contexts[user.id] = []
        
        # Track analytics
        await self.analytics.track_event(user.id, "start_command", {})
        
        # Get available AI models
        models = self.ai_client.get_available_models()
        model_text = "\n".join([f"• {info['name']} ({'Free' if info['free'] else 'Paid'})" 
                               for info in models.values()])
        
        welcome_message = f"""
🤖 **Welcome to Advanced AI Assistant!**

Hello {user.first_name}! I'm your comprehensive AI companion with these features:

**🧠 Multi-AI Support:**
{model_text}

**📱 Core Features:**
• 💬 Smart conversations with context memory
• 🖼️ Image analysis and generation
• 🎤 Voice message transcription
• 📁 File processing (PDF, documents, etc.)
• 📊 Personal analytics and insights
• 🎓 Educational assistance
• 🧠 Personal memory database

**🎯 Smart Commands:**
/help - Show all commands
/ai - Switch AI models
/profile - Your profile and stats
/settings - Customize preferences
/learn - Educational tools
/generate - Create images
/memory - Personal memory management
/export - Export your data

Just send me text, voice, images, or files - I'll handle everything intelligently!
        """
        
        await update.message.reply_text(
            welcome_message,
            parse_mode=ParseMode.MARKDOWN
        )
        
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Comprehensive help command."""
        help_text = """
🆘 **Advanced AI Assistant - Complete Guide**

**🤖 AI Models:**
/ai - Switch between AI models (Gemini, OpenAI, Anthropic)

**💬 Conversation:**
• Send any text for intelligent responses
• Context maintained throughout conversation
• Supports multiple languages

**🎤 Voice & Audio:**
• Send voice messages - I'll transcribe and respond
• Audio files supported for analysis

**🖼️ Images:**
• Send images for detailed analysis
• /generate <prompt> - Create AI images
• Image + text for multimodal responses

**📁 File Processing:**
• PDF documents - Extract and analyze text
• Code files - Review and help improve
• Data files - Analysis and insights

**🎓 Educational Tools:**
• /learn <topic> - Get structured learning materials
• Ask study questions in any subject
• Request explanations and examples

**🧠 Personal Memory:**
• /memory save <key> <value> - Save personal information
• /memory get <key> - Retrieve saved information
• /memory list - View all saved memories

**⚙️ Settings:**
• /settings - Customize bot behavior
• /profile - View your usage statistics
• /ai - Change preferred AI model

**📊 Analytics:**
• /stats - View your usage analytics
• /export - Export all your data

**🔧 Advanced Features:**
• Smart command recognition
• Rate limiting with fair usage
• Multi-language support
• Educational content generation

**Tips:**
• Be specific in your requests for better responses
• Use voice messages for hands-free interaction
• Save important information to memory for future reference
• Try different AI models for varied perspectives
        """
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
        
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show user profile and statistics."""
        user_id = update.effective_user.id
        
        # Get user from database
        user = await get_or_create_user(user_id)
        
        # Get usage statistics
        stats = await self.analytics.get_user_stats(user_id)
        
        # Get memory count
        memories = await get_user_memory(user_id)
        
        profile_text = f"""
👤 **Your Profile**

**Basic Info:**
• Name: {user.first_name or 'Not set'} {user.last_name or ''}
• Username: @{user.username or 'Not set'}
• Member since: {user.created_at.strftime('%B %d, %Y')}
• Preferred AI: {user.preferred_ai.title()}

**Usage Statistics:**
• Total messages: {stats.get('total_messages', 0)}
• AI requests: {stats.get('ai_requests', 0)}
• Images processed: {stats.get('images_processed', 0)}
• Files processed: {stats.get('files_processed', 0)}
• Voice messages: {stats.get('voice_messages', 0)}

**Personal Data:**
• Saved memories: {len(memories)}
• Last active: {user.last_active.strftime('%B %d, %Y at %H:%M')}

Use /settings to customize your experience!
        """
        
        await update.message.reply_text(profile_text, parse_mode=ParseMode.MARKDOWN)
        
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show settings menu with inline keyboard."""
        keyboard = [
            [InlineKeyboardButton("🤖 Change AI Model", callback_data="settings_ai")],
            [InlineKeyboardButton("🌐 Language Settings", callback_data="settings_language")],
            [InlineKeyboardButton("🔔 Notifications", callback_data="settings_notifications")],
            [InlineKeyboardButton("📊 Privacy Settings", callback_data="settings_privacy")],
            [InlineKeyboardButton("🗑️ Clear Data", callback_data="settings_clear")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "⚙️ **Settings Menu**\n\nChoose what you'd like to configure:",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
    async def switch_ai_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Switch AI model interface."""
        models = self.ai_client.get_available_models()
        
        keyboard = []
        for model_key, model_info in models.items():
            keyboard.append([InlineKeyboardButton(
                f"{model_info['name']} ({'Free' if model_info['free'] else 'Paid'})",
                callback_data=f"ai_switch_{model_key}"
            )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🤖 **Choose Your AI Model:**\n\nSelect the AI model you'd like to use:",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show detailed analytics."""
        user_id = update.effective_user.id
        stats = await self.analytics.get_detailed_stats(user_id)
        
        # Create usage chart data
        chart_data = await self.analytics.generate_usage_chart(user_id)
        
        stats_text = f"""
📊 **Your Analytics Dashboard**

**This Week:**
• Messages: {stats.get('week_messages', 0)}
• AI Requests: {stats.get('week_ai_requests', 0)}
• Average Response Time: {stats.get('avg_response_time', 0):.2f}s

**Most Used Features:**
• Text Chat: {stats.get('text_usage', 0)}%
• Image Processing: {stats.get('image_usage', 0)}%
• Voice Messages: {stats.get('voice_usage', 0)}%
• File Processing: {stats.get('file_usage', 0)}%

**AI Model Usage:**
• Gemini: {stats.get('gemini_usage', 0)}%
• OpenAI: {stats.get('openai_usage', 0)}%
• Anthropic: {stats.get('anthropic_usage', 0)}%

**Educational Stats:**
• Learning sessions: {stats.get('learning_sessions', 0)}
• Topics explored: {stats.get('topics_count', 0)}
• Questions asked: {stats.get('questions_count', 0)}
        """
        
        await update.message.reply_text(stats_text, parse_mode=ParseMode.MARKDOWN)
        
    async def learn_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Educational assistance command."""
        if not context.args:
            help_text = """
🎓 **Educational Assistant**

**Usage:**
/learn <topic> - Get structured learning material
/learn math algebra - Learn about algebra
/learn science physics - Physics concepts
/learn programming python - Python programming
/learn history rome - Roman history

**Features:**
• Structured lessons with examples
• Practice questions
• Visual explanations
• Progress tracking
• Personalized difficulty

**Examples:**
• /learn mathematics calculus
• /learn biology cell structure  
• /learn computer science algorithms
• /learn languages spanish basics

What would you like to learn today?
            """
            await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
            return
            
        topic = " ".join(context.args)
        user_id = update.effective_user.id
        
        # Show typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        
        # Generate educational content
        learning_content = await self.edu_assistant.generate_lesson(topic, user_id)
        
        # Track analytics
        await self.analytics.track_event(user_id, "learning_session", {"topic": topic})
        
        await update.message.reply_text(learning_content, parse_mode=ParseMode.MARKDOWN)
        
    async def generate_image_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Generate images using AI."""
        if not context.args:
            await update.message.reply_text(
                "🎨 **Image Generation**\n\n"
                "Usage: /generate <description>\n\n"
                "Examples:\n"
                "• /generate a beautiful sunset over mountains\n"
                "• /generate a futuristic city with flying cars\n"
                "• /generate a cute robot reading a book"
            )
            return
            
        prompt = " ".join(context.args)
        user_id = update.effective_user.id
        
        # Show typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_PHOTO)
        
        try:
            # Generate image
            image_url = await self.ai_client.generate_image(prompt)
            
            if image_url:
                await update.message.reply_photo(
                    photo=image_url,
                    caption=f"🎨 Generated: {prompt}"
                )
                
                # Track analytics
                await self.analytics.track_event(user_id, "image_generation", {"prompt": prompt})
            else:
                await update.message.reply_text(
                    "Sorry, I couldn't generate the image. Please check that OpenAI API is available and try again."
                )
                
        except Exception as e:
            logger.error(f"Image generation error: {e}")
            await update.message.reply_text(
                "Sorry, there was an error generating the image. Please try again later."
            )
            
    async def memory_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Personal memory management."""
        if not context.args:
            help_text = """
🧠 **Personal Memory Management**

**Commands:**
• /memory save <key> <value> - Save information
• /memory get <key> - Retrieve information  
• /memory list - Show all saved memories
• /memory delete <key> - Remove a memory
• /memory search <term> - Search memories

**Examples:**
• /memory save birthday March 15
• /memory save favorite_food Pizza
• /memory get birthday
• /memory list
• /memory search food

Your personal information is stored securely and only accessible to you!
            """
            await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
            return
            
        action = context.args[0].lower()
        user_id = update.effective_user.id
        
        if action == "save" and len(context.args) >= 3:
            key = context.args[1]
            value = " ".join(context.args[2:])
            
            await save_user_memory(user_id, key, value)
            await update.message.reply_text(f"💾 Saved: {key} = {value}")
            
        elif action == "get" and len(context.args) >= 2:
            key = context.args[1]
            memories = await get_user_memory(user_id, key)
            
            if memories:
                memory = memories[0]
                await update.message.reply_text(f"🧠 {key}: {memory['value']}")
            else:
                await update.message.reply_text(f"❌ No memory found for: {key}")
                
        elif action == "list":
            memories = await get_user_memory(user_id)
            
            if memories:
                memory_text = "🧠 **Your Memories:**\n\n"
                for memory in memories[:20]:  # Show last 20
                    memory_text += f"• **{memory['key']}**: {memory['value'][:50]}...\n"
                await update.message.reply_text(memory_text, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text("🧠 No memories saved yet!")
                
    async def export_data_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Export user data."""
        user_id = update.effective_user.id
        
        try:
            # Generate export file
            export_data = await self.analytics.export_user_data(user_id)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                import json
                json.dump(export_data, f, indent=2, default=str)
                temp_path = f.name
                
            # Send file
            with open(temp_path, 'rb') as f:
                await update.message.reply_document(
                    document=f,
                    filename=f"bot_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    caption="📁 Your complete data export"
                )
                
            # Clean up
            os.unlink(temp_path)
            
        except Exception as e:
            logger.error(f"Export error: {e}")
            await update.message.reply_text("Sorry, there was an error exporting your data.")
            
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle text messages with intelligent routing."""
        user = update.effective_user
        message_text = update.message.text
        user_id = user.id
        
        # Get user preferences
        db_user = await get_or_create_user(user_id)
        preferred_ai = db_user.preferred_ai
        
        # Check for educational queries
        if any(word in message_text.lower() for word in ['explain', 'what is', 'how to', 'teach me', 'learn']):
            response = await self.edu_assistant.handle_question(message_text, user_id)
        else:
            # Get conversation context
            if user_id not in self.user_contexts:
                self.user_contexts[user_id] = []
                
            # Add user message to context
            self.user_contexts[user_id].append({
                'role': 'user',
                'content': message_text,
                'timestamp': datetime.now(timezone.utc)
            })
            
            # Keep only last 20 messages for context
            self.user_contexts[user_id] = self.user_contexts[user_id][-20:]
            
            # Show typing indicator
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
            
            # Generate AI response
            start_time = datetime.now()
            response = await self.ai_client.generate_response(
                message_text, 
                model=preferred_ai,
                conversation_history=self.user_contexts[user_id][:-1]  # Exclude current message
            )
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Add AI response to context
            self.user_contexts[user_id].append({
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now(timezone.utc)
            })
        
        # Save to database
        await save_conversation(
            user_id=user_id,
            message=message_text,
            response=response,
            ai_model=preferred_ai,
            message_type="text"
        )
        
        # Track analytics
        await self.analytics.track_event(user_id, "text_message", {
            "ai_model": preferred_ai,
            "processing_time": processing_time,
            "message_length": len(message_text)
        })
        
        # Send response
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
        
    async def handle_voice_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle voice messages with transcription."""
        user_id = update.effective_user.id
        
        try:
            # Show typing indicator
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
            
            # Get voice file
            voice_file = await context.bot.get_file(update.message.voice.file_id)
            
            # Download audio
            audio_data = await voice_file.download_as_bytearray()
            
            # Transcribe audio
            transcript = await self.ai_client.transcribe_audio(bytes(audio_data), "ogg")
            
            if transcript:
                # Process as text message
                await update.message.reply_text(f"🎤 Transcribed: {transcript}")
                
                # Generate AI response to transcription
                db_user = await get_or_create_user(user_id)
                response = await self.ai_client.generate_response(transcript, model=db_user.preferred_ai)
                
                await update.message.reply_text(response)
                
                # Save to database
                await save_conversation(
                    user_id=user_id,
                    message=transcript,
                    response=response,
                    ai_model=db_user.preferred_ai,
                    message_type="voice"
                )
                
                # Track analytics
                await self.analytics.track_event(user_id, "voice_message", {"transcript_length": len(transcript)})
                
            else:
                await update.message.reply_text("Sorry, I couldn't transcribe the audio. Please try again.")
                
        except Exception as e:
            logger.error(f"Voice processing error: {e}")
            await update.message.reply_text("Sorry, there was an error processing your voice message.")
            
    async def handle_audio_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle audio file messages."""
        # Similar to voice message handling
        await self.handle_voice_message(update, context)
        
    async def handle_photo_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle image messages with analysis."""
        user_id = update.effective_user.id
        
        try:
            # Show typing indicator  
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
            
            # Get largest photo
            photo = update.message.photo[-1]
            photo_file = await context.bot.get_file(photo.file_id)
            
            # Download image
            image_data = await photo_file.download_as_bytearray()
            
            # Get caption or use default prompt
            caption = update.message.caption or "Analyze this image in detail."
            
            # Analyze image
            analysis = await self.ai_client.analyze_image(bytes(image_data), caption)
            
            # Save to database
            await save_conversation(
                user_id=user_id,
                message=f"[Image] {caption}",
                response=analysis,
                ai_model="multimodal",
                message_type="image"
            )
            
            # Track analytics
            await self.analytics.track_event(user_id, "image_analysis", {})
            
            await update.message.reply_text(f"🖼️ **Image Analysis:**\n\n{analysis}", parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Image processing error: {e}")
            await update.message.reply_text("Sorry, there was an error analyzing the image.")
            
    async def handle_document_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle document files."""
        user_id = update.effective_user.id
        document = update.message.document
        
        try:
            # Show typing indicator
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
            
            # Check file size (limit to 20MB)
            if document.file_size > 20 * 1024 * 1024:
                await update.message.reply_text("Sorry, file is too large. Maximum size is 20MB.")
                return
                
            # Download file
            doc_file = await context.bot.get_file(document.file_id)
            file_data = await doc_file.download_as_bytearray()
            
            # Process file
            processing_result = await self.file_processor.process_file(
                file_data=bytes(file_data),
                filename=document.file_name,
                file_type=document.mime_type
            )
            
            # Save to database
            await save_conversation(
                user_id=user_id,
                message=f"[File] {document.file_name}",
                response=processing_result,
                ai_model="file_processor",
                message_type="document"
            )
            
            # Track analytics
            await self.analytics.track_event(user_id, "file_processing", {
                "file_type": document.mime_type,
                "file_size": document.file_size
            })
            
            await update.message.reply_text(f"📁 **File Analysis:**\n\n{processing_result}", parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Document processing error: {e}")
            await update.message.reply_text("Sorry, there was an error processing the document.")
            
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle inline keyboard callbacks."""
        query = update.callback_query
        user_id = update.effective_user.id
        
        await query.answer()
        
        data = query.data
        
        if data.startswith("ai_switch_"):
            model = data.replace("ai_switch_", "")
            
            # Update user preference in database
            async with get_session() as session:
                await session.execute(
                    "UPDATE users SET preferred_ai = :model WHERE telegram_id = :user_id",
                    {"model": model, "user_id": user_id}
                )
                await session.commit()
                
            await query.edit_message_text(f"✅ AI model switched to: {model.title()}")
            
        elif data.startswith("settings_"):
            setting = data.replace("settings_", "")
            # Handle different settings
            await query.edit_message_text(f"⚙️ {setting.title()} settings - Coming soon!")
            
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Global error handler."""
        logger.error(f"Exception while handling an update: {context.error}")
        
        # Try to send error message to user
        if isinstance(update, Update) and update.effective_message:
            await update.effective_message.reply_text(
                "Sorry, an unexpected error occurred. Please try again later."
            )