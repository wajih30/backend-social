import os
import uuid
import aiofiles
from fastapi import UploadFile, HTTPException

UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp4", ".mov"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def save_upload_file(file: UploadFile) -> tuple[str, str]:
    # Validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save file using aiofiles with chunk streaming
    byte_count = 0
    try:
        async with aiofiles.open(file_path, "wb") as out_file:
            while chunk := await file.read(1024 * 1024):  # Read in 1MB chunks
                byte_count += len(chunk)
                if byte_count > MAX_FILE_SIZE:
                    # Clean up the partial file
                    await out_file.close() # Close before deleting
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    raise HTTPException(
                        status_code=400,
                        detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)} MB"
                    )
                await out_file.write(chunk)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        # Cleanup on other errors
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail="Error saving file")
    
    # Return the URL
    file_url = f"/uploads/{unique_filename}"
    
    return file_url, unique_filename
