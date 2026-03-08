from fastapi import APIRouter, File, UploadFile, HTTPException, status
from app.services.file_storage import save_file_handler

MDEIA_DIR="app/media"
router = APIRouter(prefix=("/upload"), tags=["Upload files"])

@router.post("/bytes")
async def upload_bytes(file:bytes = File(...)):
    return {
        "filename": "archivo_subido",
        "size_bytes": len(file)
    }


@router.post("/file")
async def upload_files(file:UploadFile = File(...)):
    
    return {
        "filename": file.filename,
        "content-type": file.content_type
    }


@router.post("/save")
async def save_file(file: UploadFile= File(...)):
    saved = save_file_handler(file)
    
    return saved