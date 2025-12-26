import logging
from typing import Union, Optional
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from . import schemas, version_constants

__all__ = ['DatabaseManager']

from .schemas import User

logger = logging.getLogger(version_constants.API_NAME)


class DatabaseManager:
    def __init__(self):
        self._engine = schemas.get_engine()

    @property
    def engine(self) -> Engine:
        return self._engine

    def get_user(self, user_id: int) -> Optional[schemas.User]:
        with self.create_session() as db:
            return db.query(schemas.User).filter_by(id=user_id).first()

    def create_session(self, engine: Engine = None) -> Session:
        return sessionmaker(
            bind=engine if engine else self.engine, autoflush=False
        )()

    def create_user_from_front(self, name, gender, age):
        with self.create_session() as db_session:
            existing_user = db_session.query(User).filter_by(
                first_name=name,
                gender=gender,
                age=age
            ).first()

            if existing_user:
                return existing_user

            new_user = User(first_name=name, gender=gender, age=age)
            db_session.add(new_user)
            db_session.commit()
            db_session.refresh(new_user)
            return new_user

    def save_message(self, session_id: int, sender: str, text: str, tokens: int = 0):
        with self.create_session() as db:
            try:
                new_msg = schemas.Message(
                    session_id=session_id,
                    sender=sender,  # 'user' или 'ai'
                    message_text=text,
                    token_usage=tokens
                )
                db.add(new_msg)
                db.commit()
                return new_msg
            except Exception as e:
                db.rollback()
                raise e

    def get_session_history(self, session_id: int, limit: int = 10):
        with self.create_session() as db:
            messages = db.query(schemas.Message) \
                .filter_by(session_id=session_id) \
                .order_by(schemas.Message.created_at.asc()) \
                .limit(limit) \
                .all()

            history = []
            for msg in messages:
                role = "user" if msg.sender == "user" else "assistant"
                history.append({"role": role, "content": msg.message_text})
            return history

    def get_user_by_id(self, user_id: int, session: Session = None) -> Union[schemas.User, None]:
        sess = session if session else self.create_session()
        with sess as db:
            return db.query(schemas.User).filter_by(id=user_id).first()

    def get_or_create_session(self, session_id: int, user_id: int) -> int:
        with self.create_session() as db:
            session = db.query(schemas.ChatSession).filter_by(id=session_id).first()
            if not session:
                new_session = schemas.ChatSession(
                    id=session_id,
                    user_id=user_id,
                    is_active=True
                )
                db.add(new_session)
                db.commit()
                return new_session.id
            return session.id

    def get_user_last_session(self, user_id: int) -> Optional[int]:
        with self.create_session() as db:
            session = db.query(schemas.ChatSession) \
                .filter_by(user_id=user_id) \
                .order_by(schemas.ChatSession.id.desc()) \
                .first()
            return session.id if session else None

    def create_new_session(self, user_id: int) -> int:
        with self.create_session() as db:
            new_session = schemas.ChatSession(user_id=user_id, is_active=True)
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
            return new_session.id

    def get_messages_by_session(self, session_id: int, limit: int = 50):
        with self.create_session() as db:
            return db.query(schemas.Message) \
                .filter_by(session_id=session_id) \
                .order_by(schemas.Message.created_at.asc()) \
                .limit(limit) \
                .all()