from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db
from database.crud import get_user_documents,get_document_by_id
from utils.auth import get_current_user
from services.storage_service import delete_upload_file
router=APIRouter()
@router.get('')
async def list_docs(current_user=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    return {'documents':[{'id':d.id,'filename':d.original_filename,'document_type':d.document_type,'file_size_bytes':d.file_size_bytes,'content_type':d.content_type,'uploaded_at':d.uploaded_at.isoformat()} for d in await get_user_documents(db,current_user.id)]}
@router.delete('/{doc_id}')
async def delete_doc(doc_id,current_user=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    d=await get_document_by_id(db,doc_id,current_user.id)
    if not d: raise HTTPException(404,'Document not found.')
    delete_upload_file(d.file_path); await db.delete(d); return {'deleted':True}
