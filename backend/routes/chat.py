from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db
from database.crud import create_chat_session,get_chat_sessions,get_chat_session_with_messages,add_chat_message,get_profile
from database.models import MessageRole
from utils.auth import get_current_user
from services.ai_service import career_chat
router=APIRouter()
class CreateSessionRequest(BaseModel): title:Optional[str]='New Conversation'; context_type:Optional[str]='general'
class SendMessageRequest(BaseModel): message:str=Field(min_length=1,max_length=5000)
@router.get('/sessions')
async def sessions(current_user=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    return {'sessions':[{'id':x.id,'title':x.title,'context_type':x.context_type,'updated_at':x.updated_at.isoformat()} for x in await get_chat_sessions(db,current_user.id)]}
@router.post('/sessions')
async def create(payload:CreateSessionRequest,current_user=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    x=await create_chat_session(db,current_user.id,payload.title,payload.context_type); return {'session_id':x.id,'title':x.title}
@router.get('/sessions/{session_id}')
async def get_session(session_id,current_user=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    x=await get_chat_session_with_messages(db,session_id,current_user.id)
    if not x: raise HTTPException(404,'Session not found.')
    return {'id':x.id,'title':x.title,'messages':[{'id':m.id,'role':m.role,'content':m.content,'created_at':m.created_at.isoformat()} for m in x.messages]}
@router.delete('/sessions/{session_id}')
async def delete(session_id,current_user=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    x=await get_chat_session_with_messages(db,session_id,current_user.id)
    if not x: raise HTTPException(404,'Session not found.')
    x.is_active=False; return {'archived':True}
@router.post('/sessions/{session_id}/send')
async def send(session_id,payload:SendMessageRequest,current_user=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    x=await get_chat_session_with_messages(db,session_id,current_user.id)
    if not x: raise HTTPException(404,'Session not found.')
    history=[{'role':m.role.value if hasattr(m.role,'value') else str(m.role),'content':m.content} for m in x.messages[-8:]]
    p=await get_profile(db,current_user.id); profile={'full_name':current_user.full_name,'career_goals':p.career_goals if p else '','skills':p.skills if p else [],'branch':p.branch if p else ''}
    await add_chat_message(db,session_id,MessageRole.USER,payload.message); result=await career_chat(payload.message,history,profile); msg=await add_chat_message(db,session_id,MessageRole.ASSISTANT,result['reply'],result['tokens_used']); return {'message_id':msg.id,'reply':result['reply']}
