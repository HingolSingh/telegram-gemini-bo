"""
Database models and management for the advanced bot.
"""
import os
import asyncio
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import logging

logger = logging.getLogger(__name__)

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create async engine
async_engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(async_engine, class_=AsyncSession)

Base = declarative_base()


class User(Base):
    """User model for storing user data and preferences."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    preferred_ai = Column(String(50), default="gemini")
    language = Column(String(10), default="en")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_active = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)
    settings = Column(JSON, default=dict)


class Conversation(Base):
    """Store conversation history with context."""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    message = Column(Text, nullable=False)
    response = Column(Text)
    ai_model = Column(String(50))
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    message_type = Column(String(20), default="text")  # text, voice, image, document
    metadata = Column(JSON, default=dict)


class UserMemory(Base):
    """Personal memory database for each user."""
    __tablename__ = "user_memory"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    key = Column(String(100), nullable=False)
    value = Column(Text, nullable=False)
    category = Column(String(50), default="general")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Analytics(Base):
    """Analytics and usage tracking."""
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)
    details = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    ai_model_used = Column(String(50))
    processing_time = Column(Float)


class FileUpload(Base):
    """Track uploaded files and their processing."""
    __tablename__ = "file_uploads"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    file_id = Column(String(200), nullable=False)
    file_name = Column(String(200))
    file_type = Column(String(50))
    file_size = Column(Integer)
    processed = Column(Boolean, default=False)
    processing_result = Column(Text)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


async def init_database():
    """Initialize the database and create tables."""
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


def get_session():
    """Get an async database session."""
    return async_session()


async def get_or_create_user(telegram_id: int, username: str = None, 
                           first_name: str = None, last_name: str = None):
    """Get existing user or create new one."""
    async with async_session() as session:
        try:
            from sqlalchemy import select, update
            
            # Try to find existing user
            stmt = select(User).where(User.telegram_id == telegram_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user:
                # Update last active
                stmt = update(User).where(User.telegram_id == telegram_id).values(
                    last_active=datetime.now(timezone.utc)
                )
                await session.execute(stmt)
                await session.commit()
                return user
            else:
                # Create new user
                new_user = User(
                    telegram_id=telegram_id,
                    username=username or "",
                    first_name=first_name or "",
                    last_name=last_name or ""
                )
                session.add(new_user)
                await session.commit()
                await session.refresh(new_user)
                return new_user
        except Exception as e:
            logger.error(f"Error in get_or_create_user: {e}")
            await session.rollback()
            raise


async def save_conversation(user_id: int, message: str, response: str = None, 
                          ai_model: str = None, message_type: str = "text", 
                          metadata: dict = None):
    """Save conversation to database."""
    async with async_session() as session:
        try:
            conversation = Conversation(
                user_id=user_id,
                message=message,
                response=response,
                ai_model=ai_model,
                message_type=message_type,
                metadata=metadata or {}
            )
            session.add(conversation)
            await session.commit()
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            await session.rollback()


async def get_user_memory(user_id: int, key: str = None) -> list:
    """Get user's personal memory entries."""
    async with async_session() as session:
        try:
            if key:
                result = await session.execute(
                    "SELECT * FROM user_memory WHERE user_id = :user_id AND key = :key ORDER BY updated_at DESC",
                    {"user_id": user_id, "key": key}
                )
            else:
                result = await session.execute(
                    "SELECT * FROM user_memory WHERE user_id = :user_id ORDER BY updated_at DESC LIMIT 50",
                    {"user_id": user_id}
                )
            return [dict(row._mapping) for row in result.fetchall()]
        except Exception as e:
            logger.error(f"Error getting user memory: {e}")
            return []


async def save_user_memory(user_id: int, key: str, value: str, category: str = "general"):
    """Save or update user's personal memory."""
    async with async_session() as session:
        try:
            # Check if key already exists
            result = await session.execute(
                "SELECT id FROM user_memory WHERE user_id = :user_id AND key = :key",
                {"user_id": user_id, "key": key}
            )
            existing = result.fetchone()
            
            if existing:
                # Update existing
                await session.execute(
                    "UPDATE user_memory SET value = :value, updated_at = :now WHERE id = :id",
                    {"value": value, "now": datetime.now(timezone.utc), "id": existing.id}
                )
            else:
                # Create new
                memory = UserMemory(
                    user_id=user_id,
                    key=key,
                    value=value,
                    category=category
                )
                session.add(memory)
            
            await session.commit()
        except Exception as e:
            logger.error(f"Error saving user memory: {e}")
            await session.rollback()