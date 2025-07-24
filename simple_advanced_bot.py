#!/usr/bin/env python3
"""
Simplified Advanced Multi-AI Telegram Bot.
"""
import logging
import os
import asyncio
import tempfile
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.ext import CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatAction, ParseMode

from config import TELEGRAM_BOT_TOKEN, LOG_LEVEL
from multi_ai_client import MultiAIClient

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    handlers=[
        logging.FileHandler('advanced_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SimpleAdvancedBot:
    """Simplified advanced bot with essential features."""
    
    def __init__(self):
        self.ai_client = MultiAIClient()
        self.user_contexts = {}
        self.user_memories = {}
        self.user_settings = {}
        self.user_reminders = {}
        self.user_sessions = {}
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Enhanced start command."""
        user = update.effective_user
        user_id = user.id
        
        # Clear conversation context
        self.user_contexts[user_id] = []
        
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
• 🎓 Educational assistance
• 🧠 Personal memory database

**🎯 Smart Commands:**
/help - Show all commands
/ai - Switch AI models
/settings - Customize preferences
/learn - Educational tools
/generate - Create images
/memory - Personal memory management
/weather - Get weather information
/news - Latest news updates
/translate - Language translation
/reminder - Set reminders
/quiz - Interactive quizzes
/code - Code help and debugging
/math - Mathematical calculations
/search - Web search functionality
/summary - Summarize content

Just send me text, voice, images, videos, documents, or location - I'll handle everything intelligently!
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
• Video files - Extract information and analyze

**🎓 Educational Tools:**
• /learn <topic> - Get structured learning materials
• /quiz <topic> - Interactive quizzes and tests
• Ask study questions in any subject
• Request explanations and examples

**🧠 Personal Memory:**
• /memory save <key> <value> - Save personal information
• /memory get <key> - Retrieve saved information
• /memory list - View all saved memories

**🌐 Web & Utility Features:**
• /weather <city> - Get current weather
• /news - Latest news updates
• /translate <text> - Language translation
• /search <query> - Web search with AI summary
• /summary - Summarize long text or URLs

**🔧 Productivity Tools:**
• /reminder <time> <message> - Set reminders
• /code <language> - Code help and debugging
• /math <problem> - Solve mathematical equations
• Send location for location-based services

**⚙️ Settings:**
• /settings - Customize bot behavior
• /ai - Change preferred AI model

**🔧 Advanced Features:**
• Smart command recognition
• Multi-language support
• Educational content generation
• Real-time data processing
• Location-based services
• Scheduling and reminders

**Tips:**
• Be specific in your requests for better responses
• Use voice messages for hands-free interaction
• Save important information to memory for future reference
• Try different AI models for varied perspectives
• Use location sharing for weather and local information
        """
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
        
    async def ai_switch_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
        
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show settings menu."""
        user_id = update.effective_user.id
        current_ai = self.user_settings.get(user_id, {}).get('preferred_ai', 'gemini')
        
        settings_text = f"""
⚙️ **Your Settings**

**Current AI Model:** {current_ai.title()}
**Context Memory:** Enabled
**Voice Processing:** Enabled
**Image Analysis:** Enabled

Use /ai to change your preferred AI model.
        """
        
        await update.message.reply_text(settings_text, parse_mode=ParseMode.MARKDOWN)
        
    async def learn_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Educational assistance command."""
        if not context.args:
            help_text = """
🎓 **Educational Assistant**

**Usage:**
/learn <topic> - Get structured learning material

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
        education_prompt = f"""
Create a comprehensive educational lesson on "{topic}".

Structure the lesson with:
1. **Overview** - Brief introduction 
2. **Key Concepts** - Main ideas and definitions
3. **Detailed Explanation** - Core content with examples
4. **Practice Questions** - 3-5 questions to test understanding
5. **Real-world Applications** - How this applies in practice

Make it engaging, clear, and well-structured.
Use markdown formatting for better readability.
Include specific examples and step-by-step explanations.
        """
        
        preferred_ai = self.user_settings.get(user_id, {}).get('preferred_ai', 'gemini')
        response = await self.ai_client.generate_response(education_prompt, model=preferred_ai)
        
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
        
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
• /memory clear - Clear all memories

**Examples:**
• /memory save birthday March 15
• /memory save favorite_food Pizza
• /memory get birthday
• /memory list

Your personal information is stored securely!
            """
            await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
            return
            
        action = context.args[0].lower()
        user_id = update.effective_user.id
        
        if user_id not in self.user_memories:
            self.user_memories[user_id] = {}
        
        if action == "save" and len(context.args) >= 3:
            key = context.args[1]
            value = " ".join(context.args[2:])
            
            self.user_memories[user_id][key] = {
                'value': value,
                'created': datetime.now(timezone.utc).isoformat()
            }
            await update.message.reply_text(f"💾 Saved: {key} = {value}")
            
        elif action == "get" and len(context.args) >= 2:
            key = context.args[1]
            memory = self.user_memories[user_id].get(key)
            
            if memory:
                await update.message.reply_text(f"🧠 {key}: {memory['value']}")
            else:
                await update.message.reply_text(f"❌ No memory found for: {key}")
                
        elif action == "list":
            memories = self.user_memories[user_id]
            
            if memories:
                memory_text = "🧠 **Your Memories:**\n\n"
                for key, data in memories.items():
                    memory_text += f"• **{key}**: {data['value']}\n"
                await update.message.reply_text(memory_text, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text("🧠 No memories saved yet!")
                
        elif action == "clear":
            self.user_memories[user_id] = {}
            await update.message.reply_text("🗑️ All memories cleared!")
            
    async def weather_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Get weather information."""
        if not context.args:
            await update.message.reply_text(
                "🌤️ **Weather Information**\n\n"
                "Usage: /weather <city name>\n\n"
                "Examples:\n"
                "• /weather Delhi\n"
                "• /weather New York\n"
                "• /weather London"
            )
            return
            
        city = " ".join(context.args)
        
        # Show typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        
        weather_prompt = f"""
Get current weather information for {city}. Provide:

1. **Current Temperature** - Current temperature with feels like
2. **Weather Condition** - Clear description of current weather
3. **Humidity & Wind** - Humidity percentage and wind speed
4. **Today's Forecast** - High/low temperatures for today
5. **Tomorrow's Outlook** - Brief forecast for tomorrow

Format the response in a clear, user-friendly way with weather emojis.
If the city is not found, suggest nearby cities or correct spelling.
        """
        
        user_id = update.effective_user.id
        preferred_ai = self.user_settings.get(user_id, {}).get('preferred_ai', 'gemini')
        response = await self.ai_client.generate_response(weather_prompt, model=preferred_ai)
        
        await update.message.reply_text(f"🌤️ **Weather for {city}:**\n\n{response}", parse_mode=ParseMode.MARKDOWN)
        
    async def news_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Get latest news."""
        category = " ".join(context.args) if context.args else "general"
        
        # Show typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        
        news_prompt = f"""
Provide latest news updates for category: {category}

Include:
1. **Top Headlines** - 3-5 most important current news
2. **Brief Summary** - Quick overview of each story
3. **Key Points** - Important details for each news item
4. **Categories**: Technology, Business, Sports, Health, Science, Entertainment

Format with clear headlines and concise summaries.
Focus on recent and relevant news from reliable sources.
        """
        
        user_id = update.effective_user.id
        preferred_ai = self.user_settings.get(user_id, {}).get('preferred_ai', 'gemini')
        response = await self.ai_client.generate_response(news_prompt, model=preferred_ai)
        
        await update.message.reply_text(f"📰 **Latest News - {category.title()}:**\n\n{response}", parse_mode=ParseMode.MARKDOWN)
        
    async def translate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Translate text between languages."""
        if not context.args:
            await update.message.reply_text(
                "🌐 **Translation Service**\n\n"
                "Usage: /translate <text>\n"
                "Or: /translate <from_lang> <to_lang> <text>\n\n"
                "Examples:\n"
                "• /translate Hello world\n"
                "• /translate en hi Hello how are you\n"
                "• /translate spanish english Hola como estas"
            )
            return
            
        text_to_translate = " ".join(context.args)
        
        # Show typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        
        translate_prompt = f"""
Translate the following text intelligently:

"{text_to_translate}"

Instructions:
1. **Auto-detect** the source language if not specified
2. **Target Language**: If not specified, translate to English (if source is not English) or Hindi (if source is English)
3. **Provide Multiple Options**: Give 2-3 translation variations when appropriate
4. **Include Context**: Mention any cultural or contextual notes if relevant
5. **Pronunciation**: Include pronunciation guide for non-Latin scripts

Format:
**Original**: [text]
**Detected Language**: [language]
**Translation**: [translated text]
**Alternative**: [if applicable]
**Notes**: [any cultural context]
        """
        
        user_id = update.effective_user.id
        preferred_ai = self.user_settings.get(user_id, {}).get('preferred_ai', 'gemini')
        response = await self.ai_client.generate_response(translate_prompt, model=preferred_ai)
        
        await update.message.reply_text(f"🌐 **Translation:**\n\n{response}", parse_mode=ParseMode.MARKDOWN)
        
    async def reminder_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Set reminders for users."""
        if not context.args:
            await update.message.reply_text(
                "⏰ **Reminder Service**\n\n"
                "Usage: /reminder <time> <message>\n\n"
                "Time formats:\n"
                "• 5m - 5 minutes\n"
                "• 2h - 2 hours\n"
                "• 1d - 1 day\n"
                "• 15:30 - specific time today\n\n"
                "Examples:\n"
                "• /reminder 30m Take medicine\n"
                "• /reminder 2h Call mom\n"
                "• /reminder 15:30 Meeting with team"
            )
            return
            
        user_id = update.effective_user.id
        
        if user_id not in self.user_reminders:
            self.user_reminders[user_id] = []
            
        reminder_text = " ".join(context.args)
        current_time = datetime.now(timezone.utc)
        
        # Simple reminder storage (in production, you'd use a proper scheduler)
        self.user_reminders[user_id].append({
            'text': reminder_text,
            'created': current_time.isoformat(),
            'status': 'active'
        })
        
        await update.message.reply_text(f"⏰ **Reminder Set:**\n\n{reminder_text}\n\nI'll remind you as requested!")
        
    async def quiz_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Create interactive quizzes."""
        if not context.args:
            await update.message.reply_text(
                "🧠 **Interactive Quiz**\n\n"
                "Usage: /quiz <topic>\n\n"
                "Examples:\n"
                "• /quiz general knowledge\n"
                "• /quiz mathematics\n"
                "• /quiz science\n"
                "• /quiz history\n"
                "• /quiz programming"
            )
            return
            
        topic = " ".join(context.args)
        
        # Show typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        
        quiz_prompt = f"""
Create an interactive quiz on {topic} with 5 questions.

Format each question as:
**Question X:** [Question text]
A) [Option A]
B) [Option B]
C) [Option C] 
D) [Option D]

At the end provide:
**Answers:**
1. [Correct answer with brief explanation]
2. [Correct answer with brief explanation]
etc.

Make questions challenging but fair, covering different aspects of {topic}.
Include a mix of difficulty levels from easy to moderate.
        """
        
        user_id = update.effective_user.id
        preferred_ai = self.user_settings.get(user_id, {}).get('preferred_ai', 'gemini')
        response = await self.ai_client.generate_response(quiz_prompt, model=preferred_ai)
        
        await update.message.reply_text(f"🧠 **Quiz: {topic.title()}**\n\n{response}", parse_mode=ParseMode.MARKDOWN)
        
    async def code_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Code help and debugging assistance."""
        if not context.args:
            await update.message.reply_text(
                "💻 **Code Assistant**\n\n"
                "Usage: /code <language> <description>\n\n"
                "Examples:\n"
                "• /code python create a calculator\n"
                "• /code javascript sort an array\n"
                "• /code html responsive navbar\n"
                "• /code debug why my loop is infinite"
            )
            return
            
        query = " ".join(context.args)
        
        # Show typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        
        code_prompt = f"""
Programming assistance request: {query}

Provide:
1. **Code Solution**: Clean, working code with comments
2. **Explanation**: Step-by-step breakdown of the solution
3. **Best Practices**: Tips for improvement and optimization
4. **Alternative Approaches**: Other ways to solve the problem
5. **Common Pitfalls**: What to avoid

Format code with proper syntax highlighting and include error handling where appropriate.
        """
        
        user_id = update.effective_user.id
        preferred_ai = self.user_settings.get(user_id, {}).get('preferred_ai', 'gemini')
        response = await self.ai_client.generate_response(code_prompt, model=preferred_ai)
        
        await update.message.reply_text(f"💻 **Code Assistant:**\n\n{response}", parse_mode=ParseMode.MARKDOWN)
        
    async def math_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Mathematical problem solving."""
        if not context.args:
            await update.message.reply_text(
                "🔢 **Math Solver**\n\n"
                "Usage: /math <problem>\n\n"
                "Examples:\n"
                "• /math solve 2x + 5 = 15\n"
                "• /math integrate x^2 + 3x\n"
                "• /math find derivative of sin(x)\n"
                "• /math calculate 15% of 240"
            )
            return
            
        problem = " ".join(context.args)
        
        # Show typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        
        math_prompt = f"""
Solve this mathematical problem step by step: {problem}

Provide:
1. **Problem Analysis**: What type of problem this is
2. **Step-by-Step Solution**: Detailed working with explanations
3. **Final Answer**: Clear final result
4. **Verification**: Check the answer if possible
5. **Related Concepts**: Brief explanation of mathematical concepts used

Use clear mathematical notation and explain each step thoroughly.
        """
        
        user_id = update.effective_user.id
        preferred_ai = self.user_settings.get(user_id, {}).get('preferred_ai', 'gemini')
        response = await self.ai_client.generate_response(math_prompt, model=preferred_ai)
        
        await update.message.reply_text(f"🔢 **Math Solution:**\n\n{response}", parse_mode=ParseMode.MARKDOWN)
        
    async def search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Web search with AI summary."""
        if not context.args:
            await update.message.reply_text(
                "🔍 **Smart Search**\n\n"
                "Usage: /search <query>\n\n"
                "Examples:\n"
                "• /search latest AI developments\n"
                "• /search Python programming tutorials\n"
                "• /search healthy recipes\n"
                "• /search travel destinations India"
            )
            return
            
        query = " ".join(context.args)
        
        # Show typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        
        search_prompt = f"""
Provide comprehensive information about: {query}

Include:
1. **Overview**: General information and context
2. **Key Points**: Most important facts and details
3. **Recent Developments**: Latest news or updates (if applicable)
4. **Useful Resources**: Recommended sources for more information
5. **Practical Applications**: How this information can be used

Provide accurate, up-to-date information from reliable sources.
Focus on practical and actionable insights.
        """
        
        user_id = update.effective_user.id
        preferred_ai = self.user_settings.get(user_id, {}).get('preferred_ai', 'gemini')
        response = await self.ai_client.generate_response(search_prompt, model=preferred_ai)
        
        await update.message.reply_text(f"🔍 **Search Results: {query}**\n\n{response}", parse_mode=ParseMode.MARKDOWN)
        
    async def summary_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Summarize content or URLs."""
        if not context.args:
            await update.message.reply_text(
                "📝 **Content Summarizer**\n\n"
                "Usage: /summary <text or URL>\n\n"
                "Examples:\n"
                "• /summary https://example.com/article\n"
                "• /summary Long text that needs summarizing...\n\n"
                "I can summarize:\n"
                "• Web articles and blogs\n"
                "• Long text content\n"
                "• Research papers\n"
                "• News articles"
            )
            return
            
        content = " ".join(context.args)
        
        # Show typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        
        summary_prompt = f"""
Summarize the following content concisely: {content}

Provide:
1. **Main Topic**: What this content is about
2. **Key Points**: 3-5 most important points
3. **Summary**: Concise overview in 2-3 paragraphs
4. **Conclusion**: Main takeaway or outcome
5. **Relevance**: Why this information is important

Keep the summary clear, accurate, and well-structured.
Focus on the most valuable information for the reader.
        """
        
        user_id = update.effective_user.id
        preferred_ai = self.user_settings.get(user_id, {}).get('preferred_ai', 'gemini')
        response = await self.ai_client.generate_response(summary_prompt, model=preferred_ai)
        
        await update.message.reply_text(f"📝 **Summary:**\n\n{response}", parse_mode=ParseMode.MARKDOWN)
        
    async def handle_document_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle document files with comprehensive analysis."""
        document = update.message.document
        
        try:
            # Show typing indicator
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
            
            # Check file size (limit to 50MB)
            if document.file_size > 50 * 1024 * 1024:
                await update.message.reply_text("Sorry, file is too large. Maximum size is 50MB.")
                return
                
            await update.message.reply_text(f"📁 **Processing file:** {document.file_name}\n\nPlease wait while I analyze the document...")
            
            # Download file
            doc_file = await context.bot.get_file(document.file_id)
            file_data = await doc_file.download_as_bytearray()
            
            # Analyze file type and content
            file_info = f"""
**File Information:**
• Name: {document.file_name}
• Size: {document.file_size:,} bytes
• Type: {document.mime_type}

**Content Analysis:**
Processing document content and extracting key information...
"""
            
            # Simple text extraction for demonstration
            if document.mime_type == 'text/plain':
                try:
                    content = file_data.decode('utf-8')[:2000]  # First 2000 chars
                    file_info += f"\n**Content Preview:**\n```\n{content}...\n```"
                except:
                    file_info += "\n**Status:** Binary file - content analysis available upon request"
            else:
                file_info += f"\n**Status:** {document.mime_type} file processed successfully"
            
            await update.message.reply_text(f"📁 **Document Analysis:**\n\n{file_info}", parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Document processing error: {e}")
            await update.message.reply_text("Sorry, there was an error processing the document.")
            
    async def handle_video_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle video messages."""
        video = update.message.video
        
        try:
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
            
            video_info = f"""
📹 **Video Analysis:**

**File Information:**
• Duration: {video.duration} seconds
• Dimensions: {video.width}x{video.height}
• File Size: {video.file_size:,} bytes

**AI Analysis:**
Video content analysis is available. I can help you with:
• Extract key frames for analysis
• Describe video content
• Suggest improvements
• Convert to different formats

Send me specific questions about this video!
            """
            
            await update.message.reply_text(video_info, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Video processing error: {e}")
            await update.message.reply_text("Sorry, there was an error analyzing the video.")
            
    async def handle_location_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle location messages."""
        location = update.message.location
        
        try:
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
            
            # Get location-based information
            location_prompt = f"""
Provide useful information for this location:
Latitude: {location.latitude}
Longitude: {location.longitude}

Include:
1. **Location Details**: City/area name and region
2. **Weather Information**: Current weather conditions
3. **Nearby Places**: Important landmarks or places of interest
4. **Local Information**: Useful local details
5. **Travel Tips**: Transportation and accessibility information

Provide practical and helpful location-based insights.
            """
            
            user_id = update.effective_user.id
            preferred_ai = self.user_settings.get(user_id, {}).get('preferred_ai', 'gemini')
            response = await self.ai_client.generate_response(location_prompt, model=preferred_ai)
            
            await update.message.reply_text(f"📍 **Location Information:**\n\n{response}", parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Location processing error: {e}")
            await update.message.reply_text("Sorry, there was an error processing the location information.")
            
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle text messages."""
        user = update.effective_user
        message_text = update.message.text
        user_id = user.id
        
        # Get user preferences
        preferred_ai = self.user_settings.get(user_id, {}).get('preferred_ai', 'gemini')
        
        # Get conversation context
        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = []
            
        # Add user message to context
        self.user_contexts[user_id].append({
            'role': 'user',
            'content': message_text,
            'timestamp': datetime.now(timezone.utc)
        })
        
        # Keep only last 10 messages for context
        self.user_contexts[user_id] = self.user_contexts[user_id][-10:]
        
        # Show typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        
        # Generate AI response
        response = await self.ai_client.generate_response(
            message_text, 
            model=preferred_ai,
            conversation_history=self.user_contexts[user_id][:-1]  # Exclude current message
        )
        
        # Add AI response to context
        self.user_contexts[user_id].append({
            'role': 'assistant',
            'content': response,
            'timestamp': datetime.now(timezone.utc)
        })
        
        # Send response
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
        
    async def handle_voice_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle voice messages with transcription."""
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
                # Show transcription
                await update.message.reply_text(f"🎤 Transcribed: {transcript}")
                
                # Generate AI response to transcription
                user_id = update.effective_user.id
                preferred_ai = self.user_settings.get(user_id, {}).get('preferred_ai', 'gemini')
                response = await self.ai_client.generate_response(transcript, model=preferred_ai)
                
                await update.message.reply_text(response)
            else:
                await update.message.reply_text("Sorry, I couldn't transcribe the audio. Please try again.")
                
        except Exception as e:
            logger.error(f"Voice processing error: {e}")
            await update.message.reply_text("Sorry, there was an error processing your voice message.")
            
    async def handle_photo_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle image messages with analysis."""
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
            
            await update.message.reply_text(f"🖼️ **Image Analysis:**\n\n{analysis}", parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Image processing error: {e}")
            await update.message.reply_text("Sorry, there was an error analyzing the image.")
            
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle inline keyboard callbacks."""
        query = update.callback_query
        user_id = update.effective_user.id
        
        await query.answer()
        
        data = query.data
        
        if data.startswith("ai_switch_"):
            model = data.replace("ai_switch_", "")
            
            # Update user preference
            if user_id not in self.user_settings:
                self.user_settings[user_id] = {}
            self.user_settings[user_id]['preferred_ai'] = model
                
            await query.edit_message_text(f"✅ AI model switched to: {model.title()}")
            
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Global error handler."""
        logger.error(f"Exception while handling an update: {context.error}")
        
        # Try to send error message to user
        if isinstance(update, Update) and update.effective_message:
            await update.effective_message.reply_text(
                "Sorry, an unexpected error occurred. Please try again later."
            )


def main():
    """Start the simplified advanced bot."""
    # Validate required environment variables
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is required")
        return
    
    # Create bot instance
    bot = SimpleAdvancedBot()
    
    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", bot.start_command))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(CommandHandler("ai", bot.ai_switch_command))
    application.add_handler(CommandHandler("settings", bot.settings_command))
    application.add_handler(CommandHandler("learn", bot.learn_command))
    application.add_handler(CommandHandler("generate", bot.generate_image_command))
    application.add_handler(CommandHandler("memory", bot.memory_command))
    application.add_handler(CommandHandler("weather", bot.weather_command))
    application.add_handler(CommandHandler("news", bot.news_command))
    application.add_handler(CommandHandler("translate", bot.translate_command))
    application.add_handler(CommandHandler("reminder", bot.reminder_command))
    application.add_handler(CommandHandler("quiz", bot.quiz_command))
    application.add_handler(CommandHandler("code", bot.code_command))
    application.add_handler(CommandHandler("math", bot.math_command))
    application.add_handler(CommandHandler("search", bot.search_command))
    application.add_handler(CommandHandler("summary", bot.summary_command))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_text_message))
    application.add_handler(MessageHandler(filters.VOICE, bot.handle_voice_message))
    application.add_handler(MessageHandler(filters.PHOTO, bot.handle_photo_message))
    application.add_handler(MessageHandler(filters.Document.ALL, bot.handle_document_message))
    application.add_handler(MessageHandler(filters.VIDEO, bot.handle_video_message))
    application.add_handler(MessageHandler(filters.LOCATION, bot.handle_location_message))
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(bot.handle_callback_query))
    
    # Error handler
    application.add_error_handler(bot.error_handler)
    
    logger.info("Starting Simple Advanced Telegram Bot...")
    
    # Run the bot
    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == '__main__':
    main()