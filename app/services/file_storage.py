import os
import shutil
import uuid
from fastapi import File, UploadFile, HTTPException, status


MEDIA_DIR="app/media"
ALLOW_MIME =["image/png", "image/jpeg","image/jpg"]
MAX_MB= int(os.getenv("MAX_UPLOAD_MB","10"))

def ensure_media_dir()-> None:
    os.makedirs(MEDIA_DIR, exist_ok=True)
    
def save_file_handler(file: UploadFile):
    if file.content_type not in ALLOW_MIME:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de archivo no permitido"
            )
    ensure_media_dir()
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(MEDIA_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer, length=1024*1024)
    
    size = os.path.getsize(file_path)
    if size > MAX_MB *1024 *1024:
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"Archivo demasiado grande. tamaño máximo({MAX_MB} MB)"
        )
    
    return {
        "filename": filename,
        "content_type": file.content_type,
        "url": f"/media/{filename}"
    }