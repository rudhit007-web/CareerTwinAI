from fastapi import APIRouter,Depends,HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel,EmailStr,Field
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db
from database.crud import get_user_by_email,create_user
from database.models import User
from utils.auth import hash_password,verify_password,create_access_token,get_current_user
router=APIRouter()
class RegisterRequest(BaseModel): email:EmailStr; full_name:str=Field(min_length=2,max_length=100); password:str=Field(min_length=6,max_length=128)
class TokenResponse(BaseModel): access_token:str; token_type:str='bearer'; user_id:str; full_name:str; email:str
@router.post('/register',response_model=TokenResponse,status_code=201)
async def register(payload:RegisterRequest,db:AsyncSession=Depends(get_db)):
    if await get_user_by_email(db,payload.email): raise HTTPException(400,'Email already registered.')
    u=await create_user(db,payload.email,payload.full_name,hash_password(payload.password)); return TokenResponse(access_token=create_access_token(u.id),user_id=u.id,full_name=u.full_name,email=u.email)
@router.post('/login',response_model=TokenResponse)
async def login(form:OAuth2PasswordRequestForm=Depends(),db:AsyncSession=Depends(get_db)):
    u=await get_user_by_email(db,form.username)
    if not u or not verify_password(form.password,u.hashed_password): raise HTTPException(401,'Invalid email or password.')
    if not u.is_active: raise HTTPException(403,'Account is disabled.')
    return TokenResponse(access_token=create_access_token(u.id),user_id=u.id,full_name=u.full_name,email=u.email)
@router.get('/me')
async def me(current_user:User=Depends(get_current_user)): return {'id':current_user.id,'email':current_user.email,'full_name':current_user.full_name,'is_active':current_user.is_active,'created_at':current_user.created_at.isoformat()}
