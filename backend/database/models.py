"""Database models for CareerTwin AI."""
import enum, uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Boolean, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.session import Base

def _uuid() -> str: return str(uuid.uuid4())

class ExperienceLevel(str, enum.Enum):
    STUDENT='student'; ENTRY='entry'; MID='mid'; SENIOR='senior'; EXECUTIVE='executive'
class DocumentType(str, enum.Enum):
    RESUME='resume'; OTHER='other'
class AnalysisStatus(str, enum.Enum):
    PENDING='pending'; PROCESSING='processing'; COMPLETED='completed'; FAILED='failed'
class MessageRole(str, enum.Enum):
    USER='user'; ASSISTANT='assistant'

class User(Base):
    __tablename__='users'
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=_uuid)
    email: Mapped[str]=mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str]=mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str]=mapped_column(String(255), nullable=False)
    is_active: Mapped[bool]=mapped_column(Boolean, default=True)
    created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    profile: Mapped[Optional['UserProfile']]=relationship(back_populates='user', uselist=False, cascade='all, delete-orphan')
    documents: Mapped[List['Document']]=relationship(back_populates='user', cascade='all, delete-orphan')
    resume_analyses: Mapped[List['ResumeAnalysis']]=relationship(back_populates='user', cascade='all, delete-orphan')
    skill_gap_analyses: Mapped[List['SkillGapAnalysis']]=relationship(back_populates='user', cascade='all, delete-orphan')
    roadmaps: Mapped[List['CareerRoadmap']]=relationship(back_populates='user', cascade='all, delete-orphan')
    projects: Mapped[List['ProjectRecommendation']]=relationship(back_populates='user', cascade='all, delete-orphan')
    simulations: Mapped[List['CareerSimulation']]=relationship(back_populates='user', cascade='all, delete-orphan')
    chat_sessions: Mapped[List['ChatSession']]=relationship(back_populates='user', cascade='all, delete-orphan')

class UserProfile(Base):
    __tablename__='user_profiles'
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str]=mapped_column(String(36), ForeignKey('users.id', ondelete='CASCADE'), unique=True)
    branch: Mapped[Optional[str]]=mapped_column(String(255)); semester: Mapped[Optional[str]]=mapped_column(String(50))
    cgpa: Mapped[Optional[float]]=mapped_column(Float); headline: Mapped[Optional[str]]=mapped_column(String(255))
    bio: Mapped[Optional[str]]=mapped_column(Text); location: Mapped[Optional[str]]=mapped_column(String(255)); phone: Mapped[Optional[str]]=mapped_column(String(50))
    linkedin_url: Mapped[Optional[str]]=mapped_column(String(500)); github_url: Mapped[Optional[str]]=mapped_column(String(500))
    experience_level: Mapped[Optional[str]]=mapped_column(SAEnum(ExperienceLevel)); career_goals: Mapped[Optional[str]]=mapped_column(Text)
    target_roles: Mapped[Optional[list]]=mapped_column(JSON, default=list); target_industries: Mapped[Optional[list]]=mapped_column(JSON, default=list)
    skills: Mapped[Optional[list]]=mapped_column(JSON, default=list); certifications: Mapped[Optional[list]]=mapped_column(JSON, default=list)
    education: Mapped[Optional[list]]=mapped_column(JSON, default=list); work_experience: Mapped[Optional[list]]=mapped_column(JSON, default=list)
    profile_completeness: Mapped[float]=mapped_column(Float, default=0.0); updated_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user: Mapped['User']=relationship(back_populates='profile')

class Document(Base):
    __tablename__='documents'
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=_uuid); user_id: Mapped[str]=mapped_column(String(36), ForeignKey('users.id', ondelete='CASCADE'), index=True)
    document_type: Mapped[str]=mapped_column(SAEnum(DocumentType), nullable=False); original_filename: Mapped[str]=mapped_column(String(500), nullable=False)
    file_path: Mapped[str]=mapped_column(String(1000), nullable=False); file_size_bytes: Mapped[int]=mapped_column(Integer, default=0); content_type: Mapped[str]=mapped_column(String(200))
    extracted_text: Mapped[Optional[str]]=mapped_column(Text); analysis_status: Mapped[str]=mapped_column(SAEnum(AnalysisStatus), default=AnalysisStatus.PENDING); uploaded_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
    user: Mapped['User']=relationship(back_populates='documents')

class ResumeAnalysis(Base):
    __tablename__='resume_analyses'
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=_uuid); user_id: Mapped[str]=mapped_column(String(36), ForeignKey('users.id', ondelete='CASCADE'), index=True)
    document_id: Mapped[Optional[str]]=mapped_column(String(36), ForeignKey('documents.id', ondelete='SET NULL')); summary: Mapped[Optional[str]]=mapped_column(Text)
    ats_score: Mapped[Optional[float]]=mapped_column(Float); skills_found: Mapped[Optional[list]]=mapped_column(JSON, default=list); missing_skills: Mapped[Optional[list]]=mapped_column(JSON, default=list)
    suggestions: Mapped[Optional[list]]=mapped_column(JSON, default=list); career_suggestions: Mapped[Optional[list]]=mapped_column(JSON, default=list); strengths: Mapped[Optional[list]]=mapped_column(JSON, default=list)
    experience_level: Mapped[Optional[str]]=mapped_column(String(50)); raw_result: Mapped[Optional[dict]]=mapped_column(JSON); tokens_used: Mapped[int]=mapped_column(Integer, default=0)
    status: Mapped[str]=mapped_column(SAEnum(AnalysisStatus), default=AnalysisStatus.PENDING); created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
    user: Mapped['User']=relationship(back_populates='resume_analyses')

class SkillGapAnalysis(Base):
    __tablename__='skill_gap_analyses'
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=_uuid); user_id: Mapped[str]=mapped_column(String(36), ForeignKey('users.id', ondelete='CASCADE'), index=True)
    career_goal: Mapped[str]=mapped_column(String(500), nullable=False); current_skills: Mapped[Optional[list]]=mapped_column(JSON, default=list); missing_skills: Mapped[Optional[list]]=mapped_column(JSON, default=list)
    priority_order: Mapped[Optional[list]]=mapped_column(JSON, default=list); learning_roadmap: Mapped[Optional[list]]=mapped_column(JSON, default=list); learning_resources: Mapped[Optional[list]]=mapped_column(JSON, default=list)
    weekly_plan: Mapped[Optional[list]]=mapped_column(JSON, default=list); timeline_weeks: Mapped[Optional[int]]=mapped_column(Integer); difficulty: Mapped[Optional[str]]=mapped_column(String(30)); tokens_used: Mapped[int]=mapped_column(Integer, default=0)
    status: Mapped[str]=mapped_column(SAEnum(AnalysisStatus), default=AnalysisStatus.PENDING); created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
    user: Mapped['User']=relationship(back_populates='skill_gap_analyses')

class CareerRoadmap(Base):
    __tablename__='career_roadmaps'
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=_uuid); user_id: Mapped[str]=mapped_column(String(36), ForeignKey('users.id', ondelete='CASCADE'), index=True)
    current_position: Mapped[Optional[str]]=mapped_column(String(500)); target_position: Mapped[Optional[str]]=mapped_column(String(500)); required_skills: Mapped[Optional[list]]=mapped_column(JSON, default=list)
    monthly_goals: Mapped[Optional[list]]=mapped_column(JSON, default=list); certifications: Mapped[Optional[list]]=mapped_column(JSON, default=list); expected_salary: Mapped[Optional[str]]=mapped_column(String(200))
    timeline_months: Mapped[Optional[int]]=mapped_column(Integer); future_scope: Mapped[Optional[str]]=mapped_column(Text); interview_tips: Mapped[Optional[list]]=mapped_column(JSON, default=list); key_projects: Mapped[Optional[list]]=mapped_column(JSON, default=list)
    raw_result: Mapped[Optional[dict]]=mapped_column(JSON); tokens_used: Mapped[int]=mapped_column(Integer, default=0); status: Mapped[str]=mapped_column(SAEnum(AnalysisStatus), default=AnalysisStatus.PENDING); created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
    user: Mapped['User']=relationship(back_populates='roadmaps')

class ProjectRecommendation(Base):
    __tablename__='project_recommendations'
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=_uuid); user_id: Mapped[str]=mapped_column(String(36), ForeignKey('users.id', ondelete='CASCADE'), index=True)
    title: Mapped[str]=mapped_column(String(500), nullable=False); problem_statement: Mapped[Optional[str]]=mapped_column(Text); tech_stack: Mapped[Optional[list]]=mapped_column(JSON, default=list)
    architecture: Mapped[Optional[str]]=mapped_column(Text); difficulty: Mapped[Optional[str]]=mapped_column(String(50)); timeline_weeks: Mapped[Optional[int]]=mapped_column(Integer); github_structure: Mapped[Optional[list]]=mapped_column(JSON, default=list); learning_outcomes: Mapped[Optional[list]]=mapped_column(JSON, default=list); why_this_project: Mapped[Optional[str]]=mapped_column(Text)
    tokens_used: Mapped[int]=mapped_column(Integer, default=0); created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
    user: Mapped['User']=relationship(back_populates='projects')

class CareerSimulation(Base):
    __tablename__='career_simulations'
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=_uuid); user_id: Mapped[str]=mapped_column(String(36), ForeignKey('users.id', ondelete='CASCADE'), index=True)
    option_a: Mapped[str]=mapped_column(String(255)); option_b: Mapped[str]=mapped_column(String(255)); result: Mapped[dict]=mapped_column(JSON); created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
    user: Mapped['User']=relationship(back_populates='simulations')

class ChatSession(Base):
    __tablename__='chat_sessions'
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=_uuid); user_id: Mapped[str]=mapped_column(String(36), ForeignKey('users.id', ondelete='CASCADE'), index=True); title: Mapped[str]=mapped_column(String(500), default='New Conversation')
    context_type: Mapped[str]=mapped_column(String(100), default='general'); is_active: Mapped[bool]=mapped_column(Boolean, default=True); created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow); updated_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user: Mapped['User']=relationship(back_populates='chat_sessions'); messages: Mapped[List['ChatMessage']]=relationship(back_populates='session', cascade='all, delete-orphan', order_by='ChatMessage.created_at')

class ChatMessage(Base):
    __tablename__='chat_messages'
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=_uuid); session_id: Mapped[str]=mapped_column(String(36), ForeignKey('chat_sessions.id', ondelete='CASCADE'), index=True); role: Mapped[str]=mapped_column(SAEnum(MessageRole), nullable=False); content: Mapped[str]=mapped_column(Text, nullable=False); tokens_used: Mapped[int]=mapped_column(Integer, default=0); created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
    session: Mapped['ChatSession']=relationship(back_populates='messages')
