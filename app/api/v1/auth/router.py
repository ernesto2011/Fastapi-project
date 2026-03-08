from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.api.v1.auth.repository import UserRepository
from app.core.db import get_db
from app.models.user import User
from .schemas import RoleUpdate, TokenResponse, UserCreate, UserLogin, UserPublic
from sqlalchemy.orm import Session

from app.core.security import auth2_token, create_access_token, encrypt_password, get_current_user, verify_password, require_admin

router = APIRouter(prefix="/auth", tags=['auth'])

@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(payload:UserCreate,db:Session = Depends(get_db)):
    repository = UserRepository(db)
    if repository.get_by_email(payload.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario ya existe")
    
    user = repository.create(
        email = payload.email.lower(),
        password=encrypt_password(payload.password),
        fullName=payload.fullName
    )
    db.commit()
    db.refresh(user)
    return UserPublic.model_validate(user)

@router.post('/login', response_model=TokenResponse)
async def login(payload:UserLogin, db:Session = Depends(get_db)):
    repository = UserRepository(db)
    user = repository.get_by_email(payload.email)
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credenciales invalidas"
        )
    token = create_access_token(sub=str(user.id))
    return TokenResponse(access_token=token,user=UserPublic.model_validate(user))

@router.get("/me", response_model=UserPublic)
async def me(current:User =Depends(get_current_user)):
    
    return UserPublic.model_validate(current)

@router.put("/role/{user_id}", response_model=UserPublic)
def update_role(
    user_id:int = Path(..., ge=1),
    payload: RoleUpdate = None,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin)
):
    repository = UserRepository(db)
    user = repository.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
            )
    updated = repository.set_role(user, payload.role.lower())
    db.commit()
    db.refresh(updated)
    return UserPublic.model_validate(updated)


@router.post("/token")
async def form_access_token(response = Depends(auth2_token)):
    return response