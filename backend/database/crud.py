"""Database access helpers."""
from datetime import datetime
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from database.models import *

async def get_user_by_email(db, email):
    r=await db.execute(select(User).where(User.email==email.lower().strip())); return r.scalar_one_or_none()
async def get_user_by_id(db, user_id):
    r=await db.execute(select(User).where(User.id==user_id).options(selectinload(User.profile))); return r.scalar_one_or_none()
async def create_user(db,email,full_name,hashed_password):
    user=User(email=email.lower().strip(),full_name=full_name.strip(),hashed_password=hashed_password); db.add(user); await db.flush(); db.add(UserProfile(user_id=user.id)); await db.flush(); return user

async def get_profile(db,user_id):
    r=await db.execute(select(UserProfile).where(UserProfile.user_id==user_id)); return r.scalar_one_or_none()
async def upsert_profile(db,user_id,data):
    p=await get_profile(db,user_id)
    if not p: p=UserProfile(user_id=user_id); db.add(p)
    for k,v in data.items(): setattr(p,k,v)
    p.updated_at=datetime.utcnow(); await db.flush(); return p
async def calculate_profile_completeness(p):
    if not p: return 0.0
    fields=[p.branch,p.semester,p.cgpa,p.headline,p.bio,p.location,p.career_goals,p.skills,p.education,p.target_roles]
    return round(sum(1 for x in fields if x not in (None,'',[]))/len(fields)*100,1)

async def create_document(db,**kwargs):
    d=Document(**kwargs); db.add(d); await db.flush(); return d
async def get_user_documents(db,user_id):
    r=await db.execute(select(Document).where(Document.user_id==user_id).order_by(Document.uploaded_at.desc())); return list(r.scalars().all())
async def get_document_by_id(db,doc_id,user_id):
    r=await db.execute(select(Document).where(Document.id==doc_id,Document.user_id==user_id)); return r.scalar_one_or_none()

async def create_resume_analysis(db,user_id,document_id,result,tokens_used=0):
    a=ResumeAnalysis(user_id=user_id,document_id=document_id,summary=result.get('summary'),ats_score=result.get('ats_score'),skills_found=result.get('skills_found',[]),missing_skills=result.get('missing_skills',[]),suggestions=result.get('suggestions',[]),career_suggestions=result.get('career_suggestions',[]),strengths=result.get('strengths',[]),experience_level=result.get('experience_level'),raw_result=result,tokens_used=tokens_used,status=AnalysisStatus.COMPLETED); db.add(a); await db.flush(); return a
async def get_latest_resume_analysis(db,user_id):
    r=await db.execute(select(ResumeAnalysis).where(ResumeAnalysis.user_id==user_id).order_by(ResumeAnalysis.created_at.desc()).limit(1)); return r.scalar_one_or_none()

async def create_skill_gap_analysis(db,user_id,career_goal,result,tokens_used=0):
    a=SkillGapAnalysis(user_id=user_id,career_goal=career_goal,current_skills=result.get('current_skills',[]),missing_skills=result.get('missing_skills',[]),priority_order=result.get('priority_order',[]),learning_roadmap=result.get('learning_roadmap',[]),learning_resources=result.get('learning_resources',[]),weekly_plan=result.get('weekly_plan',[]),timeline_weeks=result.get('timeline_weeks'),difficulty=result.get('difficulty'),tokens_used=tokens_used,status=AnalysisStatus.COMPLETED); db.add(a); await db.flush(); return a
async def get_latest_skill_gap(db,user_id):
    r=await db.execute(select(SkillGapAnalysis).where(SkillGapAnalysis.user_id==user_id).order_by(SkillGapAnalysis.created_at.desc()).limit(1)); return r.scalar_one_or_none()

async def create_career_roadmap(db,user_id,result,tokens_used=0):
    a=CareerRoadmap(user_id=user_id,current_position=result.get('current_position'),target_position=result.get('target_position'),required_skills=result.get('required_skills',[]),monthly_goals=result.get('monthly_goals',[]),certifications=result.get('certifications',[]),expected_salary=result.get('expected_salary'),timeline_months=result.get('timeline_months'),future_scope=result.get('future_scope'),interview_tips=result.get('interview_tips',[]),key_projects=result.get('key_projects',[]),raw_result=result,tokens_used=tokens_used,status=AnalysisStatus.COMPLETED); db.add(a); await db.flush(); return a
async def get_latest_roadmap(db,user_id):
    r=await db.execute(select(CareerRoadmap).where(CareerRoadmap.user_id==user_id).order_by(CareerRoadmap.created_at.desc()).limit(1)); return r.scalar_one_or_none()

async def create_project_recommendations(db,user_id,projects,tokens_used=0):
    out=[]
    for p in projects:
        x=ProjectRecommendation(user_id=user_id,title=p.get('title','Untitled Project'),problem_statement=p.get('problem_statement'),tech_stack=p.get('tech_stack',[]),architecture=p.get('architecture'),difficulty=p.get('difficulty'),timeline_weeks=p.get('timeline_weeks'),github_structure=p.get('github_structure',[]),learning_outcomes=p.get('learning_outcomes',[]),why_this_project=p.get('why_this_project'),tokens_used=tokens_used//max(len(projects),1)); db.add(x); out.append(x)
    await db.flush(); return out
async def get_user_projects(db,user_id):
    r=await db.execute(select(ProjectRecommendation).where(ProjectRecommendation.user_id==user_id).order_by(ProjectRecommendation.created_at.desc())); return list(r.scalars().all())

async def create_simulation(db,user_id,option_a,option_b,result):
    x=CareerSimulation(user_id=user_id,option_a=option_a,option_b=option_b,result=result); db.add(x); await db.flush(); return x
async def get_user_simulations(db,user_id):
    r=await db.execute(select(CareerSimulation).where(CareerSimulation.user_id==user_id).order_by(CareerSimulation.created_at.desc()).limit(10)); return list(r.scalars().all())

async def create_chat_session(db,user_id,title='New Conversation',context_type='general'):
    x=ChatSession(user_id=user_id,title=title or 'New Conversation',context_type=context_type or 'general'); db.add(x); await db.flush(); return x
async def get_chat_sessions(db,user_id):
    r=await db.execute(select(ChatSession).where(ChatSession.user_id==user_id,ChatSession.is_active.is_(True)).order_by(ChatSession.updated_at.desc())); return list(r.scalars().all())
async def get_chat_session_with_messages(db,session_id,user_id):
    r=await db.execute(select(ChatSession).where(ChatSession.id==session_id,ChatSession.user_id==user_id).options(selectinload(ChatSession.messages))); return r.scalar_one_or_none()
async def add_chat_message(db,session_id,role,content,tokens_used=0):
    x=ChatMessage(session_id=session_id,role=role,content=content,tokens_used=tokens_used); db.add(x); await db.execute(update(ChatSession).where(ChatSession.id==session_id).values(updated_at=datetime.utcnow())); await db.flush(); return x
