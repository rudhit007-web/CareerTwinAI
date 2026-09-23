"""Safe local file storage for development and simple deployments."""
from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile, HTTPException
from config import get_settings

settings=get_settings()
UPLOAD_DIR=Path(settings.upload_folder)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS={'.pdf','.docx','.txt'}

async def save_upload_file(file: UploadFile) -> tuple[str,int]:
    ext=Path(file.filename or '').suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400,'Unsupported file type. Use PDF, DOCX or TXT.')
    content=await file.read()
    max_bytes=settings.max_upload_size_mb*1024*1024
    if len(content)>max_bytes:
        raise HTTPException(413,f'File exceeds {settings.max_upload_size_mb} MB.')
    safe=f'{uuid4().hex}{ext}'
    path=UPLOAD_DIR/safe
    path.write_bytes(content)
    return str(path),len(content)

def delete_upload_file(file_path: str):
    p=Path(file_path)
    if p.exists(): p.unlink()
