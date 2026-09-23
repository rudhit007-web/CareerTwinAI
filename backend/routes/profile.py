from typing import Optional,List
from fastapi import APIRouter,Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db
from database.crud import get_profile,upsert_profile,calculate_profile_completeness
from utils.auth import get_current_user
router=APIRouter()
class ProfileUpdateRequest(BaseModel):
    branch:Optional[str]=None; semester:Optional[str]=None; cgpa:Optional[float]=None; headline:Optional[str]=None; bio:Optional[str]=None; location:Optional[str]=None; phone:Optional[str]=None; linkedin_url:Optional[str]=None; github_url:Optional[str]=None; experience_level:Optional[str]=None; career_goals:Optional[str]=None; skills:Optional[List[str]]=None; certifications:Optional[List[str]]=None; target_roles:Optional[List[str]]=None; target_industries:Optional[List[str]]=None
@router.get('')
async def get_profile_route(current_user=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    p=await get_profile(db,current_user.id)
    if not p:return {'profile':{}}
    return {'profile':profile_json(p,await calculate_profile_completeness(p))}
@router.put('')
async def update_profile(payload:ProfileUpdateRequest,current_user=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    data={k:v for k,v in payload.model_dump().items() if v is not None}; p=await upsert_profile(db,current_user.id,data); c=await calculate_profile_completeness(p); p.profile_completeness=c; return {'profile_completeness':c}
def profile_json(p,c): return {'branch':p.branch,'semester':p.semester,'cgpa':p.cgpa,'headline':p.headline,'bio':p.bio,'location':p.location,'phone':p.phone,'linkedin_url':p.linkedin_url,'github_url':p.github_url,'experience_level':p.experience_level,'career_goals':p.career_goals,'skills':p.skills or [],'certifications':p.certifications or [],'target_roles':p.target_roles or [],'target_industries':p.target_industries or [],'profile_completeness':c}
