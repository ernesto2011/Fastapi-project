from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field

Role = Literal["user", "editor", "admin","viewer"]

class UserBase(BaseModel):
    email: EmailStr
    fullName: Optional[str]= None
    model_config = ConfigDict(from_attributes=True)

class UserPublic(UserBase):
    id: int
    role: Role
    is_active: bool
   
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic
    
class TokenData(BaseModel):
    sub: str
    username: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str= Field(min_length=6, max_length=24)
    fullName: Optional[str]
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
class RoleUpdate(BaseModel):
    role: Role