from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Literal, Optional
from datetime import timedelta, datetime, timezone
from fastapi import Depends, HTTPException, status
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, PyJWTError
from sqlalchemy.orm import Session
from app.api.v1.auth.repository import UserRepository
from app.core.db import get_db
from app.models.user import User
from .config import settings
from pwdlib import PasswordHash

import jwt 

password_hash = PasswordHash.recommended()


credentials_exc = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="No autenticado",
    headers={"WWW-Authenticate":"Bearer"})

def raise_expired_token():
    return HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="token expired",
    headers={"WWW-Authenticate":"Bearer"})

def raise_forbidden():
    return HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Access unauthorized",
    )
def invalid_credentials():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales invalidas"
    )

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/token')

# def create_access_token(data:dict, expires_delta:Optional[timedelta]):
#     to_encode= data.copy()
#     expire = datetime.now(tz=timezone.utc)+ (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_IN))
#     to_encode.update({"exp":expire})
#     token= jwt.encode(payload=to_encode, key=settings.JWT_SECRET, algorithm=settings.JWT_ALGORITM)
#     return token
def create_access_token(sub: str, minutes: int | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=minutes or settings.ACCESS_TOKEN_EXPIRES_IN)
    return jwt.encode({"sub":sub,"exp":expire}, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITM)
    pass

def decode_token(token: str)-> dict:
    payload = jwt.decode(jwt=token, key=settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITM])
    return payload

async def get_current_user(db:Session=Depends(get_db), token: str = Depends(oauth2_scheme))-> User:

    try:
        payload = decode_token(token)
        sub: Optional[str]= payload.get("sub")
        if not sub:
           raise credentials_exc 
        user_id = int(sub)
    except ExpiredSignatureError:
        raise raise_expired_token()
    except InvalidTokenError:
        raise credentials_exc
    except PyJWTError:
        raise invalid_credentials
    
    user = db.get(User, user_id)
    
    if not user or not user.is_active:
        raise invalid_credentials
    
    return user
    
def encrypt_password(plain: str)-> str:
    return password_hash.hash(plain)

def verify_password(plain: str, encrypted: str) -> bool:
    return password_hash.verify(plain, encrypted)

def require_role(min_role:Literal["user","editor","admin","viewer"]):
    order ={"user":0, "editor":1, "admin":2, "viewer":3}
    
    def eval(user: User=Depends(get_current_user))-> User:
        if order[user.role] < order[min_role]:
            raise raise_forbidden()
        return user  
        
    return eval
async def auth2_token(form: OAuth2PasswordRequestForm= Depends(), db = Depends(get_db)):
    repository = UserRepository(db)
    user = repository.get_by_email(form.username)
    if not user or not verify_password(form.password, user.password):
        raise invalid_credentials()
    token = create_access_token(sub=str(user.id))
    return {"access_token":token, "token_type":"Bearer"}

require_user = require_role("user")
require_editor = require_role("editor")
require_admin = require_role("admin")
require_viewer = require_role("user")