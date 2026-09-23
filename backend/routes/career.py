from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db
from database.crud import *
from database.models import User
from utils.auth import get_current_user
from services.ai_service import skill_gap_analysis, generate_career_roadmap, recommend_projects, simulate_careers, interview_questions

router=APIRouter()

def profile_dict(user,profile):
    return {'full_name':user.full_name,'branch':getattr(profile,'branch',None),'semester':getattr(profile,'semester',None),'cgpa':getattr(profile,'cgpa',None),'career_goals':getattr(profile,'career_goals',None),'skills':getattr(profile,'skills',[]) or []}

def gap_json(a):
    return {'analysis_id':a.id,'career_goal':a.career_goal,'missing_skills':a.missing_skills or [],'missing_skills_count':len(a.missing_skills or []),'top_missing':[x.get('skill',x) if isinstance(x,dict) else x for x in (a.missing_skills or [])[:5]],'priority_order':a.priority_order or [],'learning_roadmap':a.learning_roadmap or [],'learning_resources':a.learning_resources or [],'weekly_plan':a.weekly_plan or [],'timeline_weeks':a.timeline_weeks,'difficulty':a.difficulty}

class SkillGapRequest(BaseModel): career_goal:str=Field(min_length=2,max_length=200); current_skills:Optional[List[str]]=None
@router.post('/skill-gap')
async def run_gap(payload:SkillGapRequest,current_user=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    p=await get_profile(db,current_user.id); skills=payload.current_skills or (p.skills if p else []) or []; result=await skill_gap_analysis(payload.career_goal,skills); tokens=result.pop('tokens_used',0); a=await create_skill_gap_analysis(db,current_user.id,payload.career_goal,result,tokens); return gap_json(a)
@router.get('/skill-gap')
async def get_gap(current_user=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    a=await get_latest_skill_gap(db,current_user.id); return gap_json(a) if a else {}

@router.post('/roadmap')
async def run_roadmap(current_user=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    p=await get_profile(db,current_user.id)
    if not p or not p.career_goals: raise HTTPException(400,'Set your career goal in Profile first.')
    result=await generate_career_roadmap(profile_dict(current_user,p)); tokens=result.pop('tokens_used',0); a=await create_career_roadmap(db,current_user.id,result,tokens); return roadmap_json(a)
@router.get('/roadmap')
async def get_roadmap(current_user=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    a=await get_latest_roadmap(db,current_user.id); return roadmap_json(a) if a else {}

def roadmap_json(a):
    return {'roadmap_id':a.id,'current_position':a.current_position,'target_position':a.target_position,'required_skills':a.required_skills or [],'monthly_goals':a.monthly_goals or [],'certifications':a.certifications or [],'expected_salary':a.expected_salary,'timeline_months':a.timeline_months,'future_scope':a.future_scope,'interview_tips':a.interview_tips or [],'key_projects':a.key_projects or []}

class ProjectsRequest(BaseModel): career_goal:Optional[str]=None
@router.post('/projects')
async def run_projects(payload:ProjectsRequest=ProjectsRequest(),current_user=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    p=await get_profile(db,current_user.id); goal=payload.career_goal or (p.career_goals if p else '') or 'Software Engineer'; skills=(p.skills if p else []) or []
    result=await recommend_projects(profile_dict(current_user,p),skills,goal); tokens=result.pop('tokens_used',0); recs=await create_project_recommendations(db,current_user.id,result.get('projects',[]),tokens); return {'projects':[project_json(x) for x in recs]}
@router.get('/projects')
async def get_projects(current_user=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    return {'projects':[project_json(x) for x in await get_user_projects(db,current_user.id)]}
def project_json(x): return {'id':x.id,'title':x.title,'problem_statement':x.problem_statement,'tech_stack':x.tech_stack or [],'technologies':x.tech_stack or [],'architecture':x.architecture,'difficulty':x.difficulty,'timeline_weeks':x.timeline_weeks,'github_structure':x.github_structure or [],'learning_outcomes':x.learning_outcomes or [],'why_this_project':x.why_this_project}

class SimulationRequest(BaseModel): option_a:str=Field(min_length=2,max_length=100); option_b:str=Field(min_length=2,max_length=100)
@router.post('/simulation')
async def simulation(payload:SimulationRequest,current_user=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    p=await get_profile(db,current_user.id); result=await simulate_careers(profile_dict(current_user,p),payload.option_a,payload.option_b); tokens=result.pop('tokens_used',0); saved=await create_simulation(db,current_user.id,payload.option_a,payload.option_b,result); return {'id':saved.id,**result}
@router.get('/simulation/history')
async def simulation_history(current_user=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    return {'simulations':[{'id':x.id,'option_a':x.option_a,'option_b':x.option_b,'result':x.result,'created_at':x.created_at.isoformat()} for x in await get_user_simulations(db,current_user.id)]}

class InterviewRequest(BaseModel): role:str=Field(min_length=2,max_length=100); difficulty:str='medium'
@router.post('/interview')
async def interview(payload:InterviewRequest,current_user=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    p=await get_profile(db,current_user.id); return await interview_questions(profile_dict(current_user,p),payload.role,payload.difficulty)
