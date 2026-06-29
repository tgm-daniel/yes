import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON
from database import Base


class QuizSession(Base):
    __tablename__ = "quiz_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4())[:8])
    profile_id = Column(String, default="vanessa")
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    current_question = Column(Integer, default=0)
    answers = Column(JSON, default=list)
    score = Column(Integer, default=0)
    finished = Column(Boolean, default=False)
    question_order = Column(JSON, default=list)


class LoginEvent(Base):
    __tablename__ = "login_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
