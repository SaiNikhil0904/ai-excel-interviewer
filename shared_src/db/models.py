"""
shared_src/db/models.py

SQLAlchemy models for the AI Excel Interviewer.
- Defines InterviewSession and InterviewTurn tables.
- Sets up relationships and default values for tracking interview progress.
"""
import uuid
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

Base = declarative_base()

class InterviewSession(Base):
    """Represents a single interview session for a candidate."""
    __tablename__ = "interview_sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, index=True)  
    current_topic = Column(String, default="Formulas")
    current_difficulty = Column(String, default="Beginner")
    question_count = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    turns = relationship(
        "InterviewTurn", 
        back_populates="session", 
        cascade="all, delete-orphan"
    )

class InterviewTurn(Base):
    """Represents a single question and answer turn in an interview session."""
    __tablename__ = "interview_turns"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("interview_sessions.id"))
    question_number = Column(Integer)
    question_text = Column(Text)
    candidate_answer = Column(Text)
    evaluation_result = Column(String) 
    feedback_text = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    session = relationship("InterviewSession", back_populates="turns")