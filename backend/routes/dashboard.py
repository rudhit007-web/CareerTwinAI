from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db
from database.crud import get_profile,calculate_profile_completeness,get_latest_resume_analysis,get_latest_skill_gap,get_latest_roadmap,get_user_projects
from utils.auth import get_current_user
router=APIRouter()
@router.get('')
async def dashboard(current_user=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    p=await get_profile(db,current_user.id); r=await get_latest_resume_analysis(db,current_user.id); g=await get_latest_skill_gap(db,current_user.id); road=await get_latest_roadmap(db,current_user.id); projects=await get_user_projects(db,current_user.id)
    pc=await calculate_profile_completeness(p); ats=r.ats_score if r else 0; missing=len(g.missing_skills or []) if g else 0; coverage=max(0,100-missing*8); readiness=round((pc+ats+coverage)/3,1)
    return {'user':{'id':current_user.id,'full_name':current_user.full_name,'email':current_user.email},'profile_completeness':pc,'career_readiness_score':readiness,'current_skills':p.skills if p else [],'resume':{'ats_score':ats,'skills_found':r.skills_found or [],'missing_skills':r.missing_skills or []} if r else None,'skill_gap':{'missing_skills_count':missing,'top_missing':[x.get('skill',x) if isinstance(x,dict) else x for x in (g.missing_skills or [])[:5]]} if g else None,'roadmap':{'current_position':road.current_position,'target_position':road.target_position,'timeline_months':road.timeline_months,'expected_salary':road.expected_salary} if road else None,'projects':[{'id':x.id,'title':x.title,'difficulty':x.difficulty,'timeline_weeks':x.timeline_weeks,'technologies':x.tech_stack or []} for x in projects[:3]]}
