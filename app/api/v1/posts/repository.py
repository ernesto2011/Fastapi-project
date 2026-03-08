from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy import select, func
from typing import Optional, Tuple, List
from app.models import PostOrm, TagORM
from math import ceil

from app.models.user import User


class PostRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, post_id: int) -> Optional[PostOrm]:
        post_find = select(PostOrm).where(PostOrm.id == post_id)
        return self.db.execute(post_find).scalar_one_or_none()

    def search(self,
               query: Optional[str],
               order_by: str,
               direction: str,
               page: int,
               per_page: int
               ) -> Tuple[int, List[PostOrm]]:
        results = select(PostOrm)

        if query:
            results = results.where(PostOrm.title.ilike(f"%{query}%"))

        total = self.db.scalar(
            select(func.count()).select_from(results.subquery())) or 0

        if total == 0:
            return 0, []

        current_page = min(page, max(1, ceil(total/per_page)))

        order_col = PostOrm.id if order_by == "id" else func.lower(
            PostOrm.title)

        results = results.order_by(
            order_col.asc() if direction == "asc" else order_col.desc())

        start = (current_page - 1) * per_page
        items = self.db.execute(results.limit(
            per_page).offset(start)).scalars().all()

        return total, items

    def by_tags(self, tags: List[str]) -> List[PostOrm]:
        normalize_tag_names = [tag.strip().lower()
                               for tag in tags if tag.strip()]

        if not normalize_tag_names:
            return []

        post_list = (
            select(PostOrm).options(
                selectinload(PostOrm.tags),
                joinedload(PostOrm.author)
            ).where(PostOrm.tags.any(func.lower(TagORM.name).in_(normalize_tag_names)))
            .order_by(PostOrm.id.asc())
        )
        return self.db.execute(post_list).scalars().all()
        
    def ensure_author(self,name:str, email:str)-> User:
    
        author_obj = self.db.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()
        if author_obj:
            return author_obj
        
        author_obj = User(name=name, email=email) 
        self.db.add(author_obj)
        self.db.flush()
    
    def ensure_tag(self, name:str)->TagORM:
        normalize = name.strip().lower()
        tag_obj = self.db.execute(
            select(TagORM).where(func.lower(TagORM.name)== normalize)
        ).scalar_one_or_none()
        if tag_obj:
            return tag_obj
        
        tag_obj = TagORM(name=name)
        self.db.add(tag_obj)
        self.db.flush()
        return tag_obj
            
    def create_post(self, title:str, content:str, author:Optional[dict], tags:List[dict], image_url:str)-> PostOrm:
        author_obj= None
        if author:
            author_obj = self.ensure_author(author['username'], author['email'])
            
        post = PostOrm(title=title, content=content, image_url=image_url, author=author_obj)
        
        names= tags[0]["name"].split(",")
        for name in names:
            name = name.strip().lower()
            if not name:
                continue
            tag_obj = self.ensure_tag(name)
            post.tags.append(tag_obj)
            
        self.db.add(post)
        self.db.flush()
        self.db.refresh(post)
        
        return post
            
    def update_post(self, post:PostOrm, updates:dict)-> PostOrm:
        for key, value in updates.items():
            setattr(post, key, value)
        
        self.db.add(post)
        self.db.refresh(post)
        
        return post
    
    def delete_post(self, post:PostOrm)->None:
        self.db.delete(post)