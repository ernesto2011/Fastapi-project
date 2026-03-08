from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.v1.auth import repository
from app.api.v1.categories.repository import CategoryRepository
from app.core.db import get_db
from sqlalchemy.exc import SQLAlchemyError
from app.api.v1.categories.schemas import CategoryCreate, CategoryUpdate, CategoryPublic

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryPublic])
def list_categories(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    repostory = CategoryRepository(db)
    return repostory.list_many(skip=skip, limit=limit)



@router.post("", response_model=CategoryPublic, status_code=status.HTTP_201_CREATED)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    repository = CategoryRepository(db)
    exists = repository.get_by_slug(data.slug.lower())
    if exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Esta categoria ya existe")
    category = repository.create(name=data.name, slug=data.slug.lower())
    db.commit()
    db.refresh(category)
    return category

@router.get("/{category_id}", response_model=CategoryPublic)
def get_category(category_id: int, db: Session = Depends(get_db)):
    repository = CategoryRepository(db)
    category = repository.get(category_id=category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Categoria no encontrada con el id: {category_id}")
    return category

@router.put("/{category_id}", response_model=CategoryPublic)
def update_category(category_id: int, data: CategoryUpdate, db: Session = Depends(get_db)):
    repository = CategoryRepository(db)
    category = repository.get(category_id=category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Categoria no encontrada con el id: {category_id}")
    updated= repository.update(category, data.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(updated)
    return updated
    
@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    repository = CategoryRepository(db)
    category = repository.get(category_id=category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Categoria no encontrada con el id: {category_id}")
    try:
        repository.delete(category)
        db.commit()
        return None
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error al eliminar la categoria")
    
    