from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base
from .user import User  # Importer User au lieu de le redéfinir
import enum

class MeetingStatus(enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Meeting(Base):
    __tablename__ = "meetings"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    zoom_meeting_id = Column(String, unique=True)
    title = Column(String)
    scheduled_time = Column(DateTime)
    duration_minutes = Column(Integer)
    status = Column(Enum(MeetingStatus), default=MeetingStatus.SCHEDULED)
    participants = Column(JSON, default=[], nullable=True)  # List of participant objects
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="meetings")
    transcription = relationship("Transcription", back_populates="meeting", uselist=False, cascade="all, delete-orphan")
    action_items = relationship("ActionItem", back_populates="meeting", cascade="all, delete-orphan")
    summary = relationship("Summary", back_populates="meeting", uselist=False, cascade="all, delete-orphan")

class Transcription(Base):
    __tablename__ = "transcriptions"
    
    id = Column(Integer, primary_key=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), unique=True)
    full_text = Column(String)
    speaker_segments = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    meeting = relationship("Meeting", back_populates="transcription")

class ActionItem(Base):
    __tablename__ = "action_items"
    
    id = Column(Integer, primary_key=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"))
    description = Column(String)
    assigned_to = Column(String, nullable=True)
    due_date = Column(DateTime, nullable=True)  # Date limite
    deadline = Column(String, nullable=True)  # Keep for backward compatibility
    priority = Column(String, default="medium")  # low, medium, high
    status = Column(String, default="todo")  # todo, in_progress, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    meeting = relationship("Meeting", back_populates="action_items")

class Summary(Base):
    __tablename__ = "summaries"
    
    id = Column(Integer, primary_key=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), unique=True)
    executive_summary = Column(String)
    decisions = Column(JSON)
    questions = Column(JSON)
    full_markdown = Column(String)
    pdf_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    meeting = relationship("Meeting", back_populates="summary")