import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, Date, ForeignKey
from database import Base


class Profile(Base):
    __tablename__ = "profiles"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4())[:12])
    type = Column(String, default="quiz")
    display_name = Column(String, default="")
    data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)


class LoginCredential(Base):
    __tablename__ = "login_credentials"
    id = Column(Integer, primary_key=True, autoincrement=True)
    login_name = Column(String, unique=True, nullable=False)
    profile_id = Column(String, ForeignKey("profiles.id"), nullable=False)
    password_hash = Column(String, nullable=False)


class LoginEvent(Base):
    __tablename__ = "login_events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


class Couple(Base):
    __tablename__ = "couples"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4())[:8])
    user1_id = Column(String, nullable=False)
    user2_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class DiaryEntry(Base):
    __tablename__ = "diary_entries"
    id = Column(Integer, primary_key=True, autoincrement=True)
    couple_id = Column(String, index=True, nullable=False)
    author_id = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    content = Column(Text, default="")
    mood = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)


class DailyQuestion(Base):
    __tablename__ = "daily_questions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    couple_id = Column(String, index=True, nullable=False)
    date = Column(Date, nullable=False)
    question_pt = Column(String, nullable=False)
    question_en = Column(String, nullable=False)
    answer_a = Column(Text, nullable=True)
    answer_b = Column(Text, nullable=True)
    seen_by_a = Column(Boolean, default=False)
    seen_by_b = Column(Boolean, default=False)


class Challenge(Base):
    __tablename__ = "challenges"
    id = Column(Integer, primary_key=True, autoincrement=True)
    couple_id = Column(String, index=True, nullable=False)
    date = Column(Date, nullable=False)
    type = Column(String, nullable=False)
    data = Column(JSON, default=dict)
    created_by = Column(String, nullable=True)
    guess_a = Column(Text, nullable=True)
    guess_b = Column(Text, nullable=True)
    answered_a = Column(Boolean, default=False)
    answered_b = Column(Boolean, default=False)
    seen_a = Column(Boolean, default=False)
    seen_b = Column(Boolean, default=False)
    done_a = Column(Boolean, default=False)
    done_b = Column(Boolean, default=False)


class AgendaEvent(Base):
    __tablename__ = "agenda_events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    couple_id = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    description = Column(Text, default="")
    created_by = Column(String, nullable=False)


class TodoItem(Base):
    __tablename__ = "todo_items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    couple_id = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, default="")
    done = Column(Boolean, default=False)
    done_by = Column(String, nullable=True)
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class WeeklyReview(Base):
    __tablename__ = "weekly_reviews"
    id = Column(Integer, primary_key=True, autoincrement=True)
    couple_id = Column(String, index=True, nullable=False)
    week_start = Column(Date, nullable=False)
    reflection_a = Column(Text, nullable=True)
    reflection_b = Column(Text, nullable=True)
    completed = Column(Boolean, default=False)


class QuizAnswer(Base):
    __tablename__ = "quiz_answers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    couple_id = Column(String, index=True, nullable=False)
    author_id = Column(String, nullable=False)
    question_idx = Column(Integer, nullable=False)
    category = Column(String, default="basic")
    about_self = Column(Text, nullable=True)
    about_partner = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class QuoteRefresh(Base):
    __tablename__ = "quote_refreshes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    couple_id = Column(String, index=True, nullable=False)
    date = Column(Date, nullable=False)
    current_offset = Column(Integer, default=0)
    max_offset = Column(Integer, default=0)
    unlock_count = Column(Integer, default=0)
    liked_offset = Column(Integer, nullable=True)


class Photo(Base):
    __tablename__ = "photos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    couple_id = Column(String, index=True, nullable=False)
    author_id = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    data = Column(Text, nullable=False)  # base64-encoded JPEG
    caption = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
