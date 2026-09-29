from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Boolean
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import create_engine
import os

BASE = declarative_base()

class User(BASE):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(256), unique=True, nullable=False, index=True)
    hashed_password = Column(Text, nullable=False)
    role = Column(String(32), nullable=False)  # 'teacher' or 'student'
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Adaptive learning fields
    performance_level = Column(String(32), default="average")  # 'struggling', 'average', 'advanced'
    avg_quiz_score = Column(Float, default=0.0)

    students = relationship("User", backref="teacher", remote_side=[id])
    messages = relationship("Message", backref="user", cascade="all, delete-orphan")
    homework_sessions = relationship("HomeworkSession", backref="user", cascade="all, delete-orphan")
    quiz_attempts = relationship("QuizAttempt", backref="user", cascade="all, delete-orphan")

class Message(BASE):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role = Column(String(32), nullable=False) # 'user' or 'ai'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class HomeworkSession(BASE):
    __tablename__ = "homework_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    problem = Column(Text, nullable=False)
    solution = Column(Text, nullable=True)
    hint_count = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)

class QuizAttempt(BASE):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    score = Column(Float, nullable=False)
    total_questions = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    questions = relationship("QuizQuestion", backref="quiz_attempt", cascade="all, delete-orphan")

class QuizQuestion(BASE):
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_attempt_id = Column(Integer, ForeignKey("quiz_attempts.id"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    correct_answer = Column(Text, nullable=False)
    user_answer = Column(Text, nullable=True)
    is_correct = Column(Boolean, default=False)

def get_engine(db_path: str | None = None):
    if db_path is None:
        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(current_dir)
        db_file = os.path.join(project_root, "ai_tutor.db")
        db_path = f"sqlite:///{db_file}"
    return create_engine(db_path, connect_args={"check_same_thread": False})

def create_tables(engine=None):
    if engine is None:
        engine = get_engine()
    BASE.metadata.create_all(engine)
