from sqlalchemy import String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from database import Base

class Topic(Base):
    __tablename__="topics"
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(120),unique=True,index=True)
    description: Mapped[str]=mapped_column(Text)
    questions=relationship("Question",back_populates="topic",cascade="all, delete-orphan")

class Question(Base):
    __tablename__="questions"
    id: Mapped[int]=mapped_column(primary_key=True)
    topic_id: Mapped[int]=mapped_column(ForeignKey("topics.id"),index=True)
    subtopic: Mapped[str]=mapped_column(String(100),default="General")
    question: Mapped[str]=mapped_column(Text,unique=True)
    options: Mapped[list]=mapped_column(JSON)
    correct_index: Mapped[int]=mapped_column(Integer)
    explanation: Mapped[str]=mapped_column(Text)
    difficulty: Mapped[str]=mapped_column(String(20),default="Beginner")
    source_url: Mapped[str]=mapped_column(String(500),default="")
    is_approved: Mapped[bool]=mapped_column(Boolean,default=True)
    topic=relationship("Topic",back_populates="questions")

class LessonProgress(Base):
    __tablename__="lesson_progress"
    id: Mapped[int]=mapped_column(primary_key=True)
    learner: Mapped[str]=mapped_column(String(80),default="local-learner",index=True)
    topic_name: Mapped[str]=mapped_column(String(120),index=True)
    completed: Mapped[bool]=mapped_column(Boolean,default=False)
    updated_at: Mapped[str]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())

class QuizAttempt(Base):
    __tablename__="quiz_attempts"
    id: Mapped[int]=mapped_column(primary_key=True)
    learner: Mapped[str]=mapped_column(String(80),default="local-learner",index=True)
    topic_name: Mapped[str]=mapped_column(String(120))
    total: Mapped[int]=mapped_column(Integer)
    correct: Mapped[int]=mapped_column(Integer)
    accuracy: Mapped[float]=mapped_column(Float)
    points: Mapped[int]=mapped_column(Integer,default=0)
    created_at: Mapped[str]=mapped_column(DateTime(timezone=True),server_default=func.now())

class UserQuestion(Base):
    __tablename__="user_questions"
    id: Mapped[int]=mapped_column(primary_key=True)
    learner: Mapped[str]=mapped_column(String(80),default="local-learner")
    topic_name: Mapped[str]=mapped_column(String(120))
    subtopic: Mapped[str]=mapped_column(String(100))
    question: Mapped[str]=mapped_column(Text)
    options: Mapped[list]=mapped_column(JSON)
    correct_index: Mapped[int]=mapped_column(Integer)
    explanation: Mapped[str]=mapped_column(Text)
    difficulty: Mapped[str]=mapped_column(String(20),default="Beginner")


class User(Base):
    __tablename__="users"
    id: Mapped[str]=mapped_column(String(36),primary_key=True)
    username: Mapped[str]=mapped_column(String(40),unique=True,index=True)
    email: Mapped[str]=mapped_column(String(254),unique=True,index=True)
    password_hash: Mapped[str]=mapped_column(String(256))
    is_guest: Mapped[bool]=mapped_column(Boolean,default=False)
    created_at: Mapped[str]=mapped_column(DateTime(timezone=True),server_default=func.now())
