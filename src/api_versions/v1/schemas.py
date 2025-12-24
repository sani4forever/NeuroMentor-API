"""
SQLAlchemy schemas for API version 1.
"""

from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    Text,
    create_engine,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine import Engine, URL
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from . import version_constants

__all__ = [
    'User', 'ChatSession', 'Message', 'AIRequest',
    'Subscription', 'UsageLog', 'Admin',
    'get_engine'
]

Base = declarative_base()

def get_engine() -> Engine:
    """Get the engine for the database."""
    if not version_constants.POSTGRES_NAME:
        raise ValueError('POSTGRES_NAME is not set')

    url = URL.create(
        drivername='postgresql+psycopg2',
        host=version_constants.POSTGRES_HOST,
        port=version_constants.POSTGRES_PORT,
        username=version_constants.POSTGRES_USER,
        password=version_constants.POSTGRES_PASSWORD,
        database=version_constants.POSTGRES_NAME
    )

    try:
        engine = create_engine(url, echo=False)
        Base.metadata.create_all(engine)
    except OperationalError:
        connection = psycopg2.connect(
            dbname='postgres',
            user=version_constants.POSTGRES_USER,
            password=version_constants.POSTGRES_PASSWORD,
            host=version_constants.POSTGRES_HOST,
            port=version_constants.POSTGRES_PORT,
        )
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        cursor.execute(f'CREATE DATABASE {version_constants.POSTGRES_NAME};')
        cursor.close()
        connection.close()

        engine = create_engine(url, echo=False)
        Base.metadata.create_all(engine)

    return engine


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=True, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True) # Mapping "name" from frontend here
    last_name = Column(String(255), nullable=True)
    gender = Column(String(50), nullable=True)
    age = Column(Integer, nullable=True) # Added to store frontend data
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    usage_logs = relationship("UsageLog", back_populates="user")
    admin_profile = relationship("Admin", back_populates="user", uselist=False)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, first_name={self.first_name})>"


class ChatSession(Base):
    __tablename__ = 'chat_sessions'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('chat_sessions.id'), nullable=False)
    sender = Column(String(50), nullable=False)  # 'user' or 'ai'
    message_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    token_usage = Column(Integer, default=0)

    session = relationship("ChatSession", back_populates="messages")
    ai_request = relationship("AIRequest", back_populates="message", uselist=False)


class AIRequest(Base):
    __tablename__ = 'ai_requests'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey('messages.id'), nullable=False)
    request_payload = Column(JSONB, nullable=True)
    response_payload = Column(JSONB, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    status_code = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    message = relationship("Message", back_populates="ai_request")


class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    plan_name = Column(String(50), default="free")
    is_active = Column(Boolean, default=True)
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    end_date = Column(DateTime(timezone=True), nullable=True)
    usage_limit = Column(Integer, default=100)
    used_requests = Column(Integer, default=0)
    auto_renew = Column(Boolean, default=False)

    user = relationship("User", back_populates="subscriptions")


class UsageLog(Base):
    __tablename__ = 'usage_logs'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now())
    requests_count = Column(Integer, default=0)
    tokens_used = Column(Integer, default=0)
    session_count = Column(Integer, default=0)

    user = relationship("User", back_populates="usage_logs")


class Admin(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    role = Column(String(50), default="moderator")  # owner, admin, moderator
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="admin_profile")