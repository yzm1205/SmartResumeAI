import os
import logging
import sqlite3
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

logger = logging.getLogger(__name__)

# Get database path from environment variables
DB_PATH = os.getenv("DATABASE_PATH", "data/resume_db.sqlite")

# Create SQLAlchemy engine and session
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Define database models
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Resume sections as relationships
    experiences = relationship("Experience", back_populates="user", cascade="all, delete-orphan")
    educations = relationship("Education", back_populates="user", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="user", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    publications = relationship("Publication", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("Achievement", back_populates="user", cascade="all, delete-orphan")
    
    # Basic info
    name = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(String(255))
    linkedin = Column(String(255))
    github = Column(String(255))
    website = Column(String(255))
    summary = Column(Text)

class Experience(Base):
    __tablename__ = 'experiences'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="experiences")
    
    company = Column(String(100))
    title = Column(String(100))
    location = Column(String(100))
    start_date = Column(String(50))
    end_date = Column(String(50))
    description = Column(Text)
    achievements = Column(Text)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Education(Base):
    __tablename__ = 'educations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="educations")
    
    institution = Column(String(100))
    degree = Column(String(100))
    field_of_study = Column(String(100))
    location = Column(String(100))
    start_date = Column(String(50))
    end_date = Column(String(50))
    gpa = Column(String(20))
    description = Column(Text)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Skill(Base):
    __tablename__ = 'skills'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="skills")
    
    name = Column(String(100))
    category = Column(String(100))
    proficiency = Column(String(50))
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Certification(Base):
    __tablename__ = 'certifications'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="certifications")
    
    name = Column(String(100))
    issuer = Column(String(100))
    date = Column(String(50))
    description = Column(Text)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="projects")
    
    name = Column(String(100))
    description = Column(Text)
    technologies = Column(String(255))
    url = Column(String(255))
    start_date = Column(String(50))
    end_date = Column(String(50))
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Publication(Base):
    __tablename__ = 'publications'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="publications")
    
    title = Column(String(255))
    publisher = Column(String(100))
    date = Column(String(50))
    url = Column(String(255))
    description = Column(Text)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Achievement(Base):
    __tablename__ = 'achievements'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="achievements")
    
    title = Column(String(255))
    date = Column(String(50))
    description = Column(Text)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class JobDescription(Base):
    __tablename__ = 'job_descriptions'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    company = Column(String(100))
    description = Column(Text)
    original_text = Column(Text)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

def init_database():
    """Initialize the SQLite database."""
    try:
        # Create database directory if it doesn't exist
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
        # Create tables
        Base.metadata.create_all(engine)
        logger.info(f"Database initialized successfully at {DB_PATH}")
        
        return True
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        return False

def get_session():
    """Get a database session."""
    return Session() 