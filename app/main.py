import os
from fastapi import FastAPI
from app.core.db import Base,engine, wait_for_db
from dotenv import load_dotenv
from app.api.v1.posts.router import router as post_router
from app.api.v1.auth.router import router as auth_router
from app.api.v1.uploads.router import router as uploads_router
from app.api.v1.tags.router import router as tag_router
from fastapi.staticfiles import StaticFiles
load_dotenv()
MEDIA_DIR= "app/media"

def create_app() -> FastAPI:
    app = FastAPI(title="Mini blog")
    wait_for_db(engine)
    Base.metadata.create_all(bind=engine)
    
    app.include_router(auth_router, prefix='/api/v1')
    app.include_router(post_router)
    app.include_router(uploads_router, prefix="/api/v1")
    app.include_router(tag_router, prefix="/api/v1")
    os.makedirs(MEDIA_DIR, exist_ok=True)
    app.mount('/media', StaticFiles(directory=MEDIA_DIR), name="media")
    return app

app = create_app()


    