from fastapi import APIRouter, UploadFile, File, Depends
from app.api.deps import get_current_user
from app.models.user import User
from app.services import file_service

router = APIRouter()

@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a file (image/video) and return its URL.
    """
    file_url, filename = await file_service.save_upload_file(file)
    
    return {"url": file_url, "filename": filename}
