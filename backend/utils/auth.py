"""JWT and password utilities."""
from datetime import datetime, timedelta, timezone
from typing import Optional
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from config import get_settings
from database.session import get_db
from database.crud import get_user_by_id

settings=get_settings(); ALGORITHM='HS256'; oauth2_scheme=OAuth2PasswordBearer(tokenUrl='/api/auth/login')

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(),bcrypt.gensalt()).decode()
def verify_password(password: str, hashed: str) -> bool:
    try: return bcrypt.checkpw(password.encode(),hashed.encode())
    except Exception: return False

def create_access_token(user_id: str, expires_delta: Optional[timedelta]=None) -> str:
    now=datetime.now(timezone.utc); exp=now+(expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    return jwt.encode({'sub':user_id,'iat':now,'exp':exp},settings.secret_key,algorithm=ALGORITHM)

def decode_access_token(token: str):
    try: return jwt.decode(token,settings.secret_key,algorithms=[ALGORITHM]).get('sub')
    except JWTError: return None

async def get_current_user(token: str=Depends(oauth2_scheme), db=Depends(get_db)):
    uid=decode_access_token(token)
    if not uid: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Invalid or expired token.',headers={'WWW-Authenticate':'Bearer'})
    user=await get_user_by_id(db,uid)
    if not user or not user.is_active: raise HTTPException(status_code=401,detail='User not found or inactive.')
    return user
