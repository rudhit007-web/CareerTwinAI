from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db
from database.crud import create_document, get_user_documents, create_resume_analysis, get_latest_resume_analysis, get_profile
from database.models import User, DocumentType
from utils.auth import get_current_user
from services.storage_service import save_upload_file
from services.document_service import extract_text
from services.ai_service import analyze_resume

router=APIRouter()

@router.post('/upload')
async def upload_resume(file: UploadFile=File(...), current_user:User=Depends(get_current_user), db:AsyncSession=Depends(get_db)):
    path,size=await save_upload_file(file)
    try: text=extract_text(path,file.content_type)
    except Exception as exc:
        from services.storage_service import delete_upload_file; delete_upload_file(path); raise HTTPException(400,str(exc))
    if len(text.strip())<80: raise HTTPException(400,'Could not extract enough text from this file.')
    doc=await create_document(db,user_id=current_user.id,document_type=DocumentType.RESUME,original_filename=file.filename or 'resume',file_path=path,file_size_bytes=size,content_type=file.content_type or 'application/octet-stream',extracted_text=text)
    return {'document_id':doc.id,'filename':doc.original_filename,'extracted_chars':len(text),'status':'uploaded'}

@router.post('/analyze')
async def analyze_latest_resume(current_user:User=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    docs=await get_user_documents(db,current_user.id); docs=[d for d in docs if d.document_type==DocumentType.RESUME and d.extracted_text]
    if not docs: raise HTTPException(404,'Upload a resume first.')
    profile=await get_profile(db,current_user.id); goal=profile.career_goals if profile else ''
    result=await analyze_resume(docs[0].extracted_text,goal); tokens=result.pop('tokens_used',0)
    a=await create_resume_analysis(db,current_user.id,docs[0].id,result,tokens)
    return serialize(a)

@router.get('')
async def latest_resume(current_user:User=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    a=await get_latest_resume_analysis(db,current_user.id); return serialize(a) if a else {}

def serialize(a):
    if not a: return {}
    return {'analysis_id':a.id,'summary':a.summary,'ats_score':a.ats_score,'skills_found':a.skills_found or [],'missing_skills':a.missing_skills or [],'suggestions':a.suggestions or [],'career_suggestions':a.career_suggestions or [],'strengths':a.strengths or [],'experience_level':a.experience_level}
