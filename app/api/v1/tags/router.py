from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm  import Session
from sqlalchemy.exc import SQLAlchemyError
from app.api.v1.tags.repository import Tagrepository
from app.api.v1.tags.schemas import TagCreate, TagPublic, TagUpdate
from app.core.db import get_db
from app.core.security import get_current_user, require_editor, require_admin
from app.models.user import User


router= APIRouter(prefix="/tags", tags=["tags"])

@router.post("", response_model=TagPublic, response_description="Tag creado", status_code=status.HTTP_201_CREATED)
def create_tag(tag: TagCreate, db: Session  = Depends(get_db), _editor: User = Depends(require_editor)):
    repository= Tagrepository(db)
    try:
      tag_created = repository.create_tag(name=tag.name)
      db.commit()
      db.refresh(tag_created)
      return tag_created
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear el tag")

@router.get("", response_model=dict)
def list_tags(
  page: int = Query(1, ge=1),
  per_page: int =Query(10, ge=1, le=100),
  order_by: str = Query("id", pattern="^(id|name)$"),
  direction: str = Query("asc", pattern="^(asc|desc)$"),
  search: str | None =Query(None),
  db: Session = Depends(get_db)
  ):
  repository = Tagrepository(db)
  return repository.list_tags(
    search = search,
    order_by = order_by,
    direction = direction,
    page = page,
    per_page = per_page
  )
  
@router.put("/{tag_id}", response_model=TagPublic, response_description="Tag actualizado")
def update_tag(
  tag_id: int,payload:TagUpdate, db: Session  = Depends(get_db), _editor: User = Depends(require_editor)):
  repository= Tagrepository(db)
  tag = repository.update(tag_id=tag_id, name=payload.name)
  if tag is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tag con id:{tag_id} no encontrado")
  try:
    db.commit()
    return TagPublic.model_validate(tag)
  except SQLAlchemyError:
    db.rollback()
    raise HTTPException(status_code=500, detail="Error al actualizar el TAG")
  
@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, db: Session= Depends(get_db), _admin:User= Depends(require_admin)):
  repository= Tagrepository(db)
  tag = repository.delete(tag_id)
  if tag is not True:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag no encontrado")
  
  try:
    db.commit()
    return
  except SQLAlchemyError:
    db.rollback()
    raise HTTPException(status_code=500, detail="Error al eliminar el tag")
  
@router.get("/most-popular")
def get_most_popular_tag(
  db: Session = Depends(get_db),
):
  repository = Tagrepository(db)
  popular_tag = repository.most_popular()
  
  if not popular_tag:
    raise HTTPException(status_code=404, detail='No hay tags disponibles en este momento')
  
  return popular_tag
