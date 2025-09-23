from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import json

Base = declarative_base()

class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vapi_call_id = Column(String(255), unique=True, nullable=True)
    candidate_phone = Column(String(20), nullable=False)
    candidate_name = Column(String(100), nullable=True)
    position = Column(String(100), default="Software Developer")
    
    # Call Status
    status = Column(String(50), default="pending")  # pending, in_progress, completed, failed
    call_duration = Column(Integer, nullable=True)  # Sekunden
    
    # Interview Data
    transcript = Column(Text, nullable=True)
    recording_url = Column(String(500), nullable=True)
    
    # Evaluation Results  
    evaluation_score = Column(Float, nullable=True)
    evaluation_data = Column(Text, nullable=True)  # JSON als Text gespeichert
    recommendation = Column(String(50), nullable=True)  # EINLADEN, ABLEHNEN, UNENTSCHIEDEN
    
    # HR Processing
    hr_notified = Column(Boolean, default=False)
    slack_message_ts = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    call_started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Notes and Follow-up
    hr_notes = Column(Text, nullable=True)
    next_steps = Column(String(200), nullable=True)
    
    def set_evaluation_data(self, data):
        """Helper zum Setzen von JSON-Daten"""
        self.evaluation_data = json.dumps(data)
    
    def get_evaluation_data(self):
        """Helper zum Abrufen von JSON-Daten"""
        if self.evaluation_data:
            return json.loads(self.evaluation_data)
        return {}

class Candidate(Base):
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    phone = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=True)
    email = Column(String(150), nullable=True)
    
    # Application Info
    position_applied = Column(String(100), nullable=True)
    application_source = Column(String(100), nullable=True)  # Website, LinkedIn, etc.
    cv_url = Column(String(500), nullable=True)
    
    # Interview History
    total_interviews = Column(Integer, default=0)
    last_interview_date = Column(DateTime, nullable=True)
    
    # Status
    status = Column(String(50), default="new")  # new, interviewed, hired, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class SystemConfig(Base):
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=True)
    description = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    def __init__(self):
        # SQLite für Demo/Test (einfach und problemlos)
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'interview_agent.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        db_url = f"sqlite:///{db_path}"
        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
    def create_tables(self):
        Base.metadata.create_all(self.engine)
        
    def get_session(self):
        return self.SessionLocal()