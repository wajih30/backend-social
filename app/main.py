from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import traceback
import os
from app.api import auth, users, social, notifications, upload, ai

# Setup basic logging to file
logging.basicConfig(filename='backend_error.log', level=logging.ERROR)

app = FastAPI(title="Social Media App API")

# Expanded CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Serve static files (uploads)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_msg = f"Global Exception: {str(exc)}\n{traceback.format_exc()}"
    logging.error(error_msg)
    print(error_msg) # Print to console too for redundancy
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error. Check server logs."},
    )

app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(social.router, prefix="/social", tags=["social"])
app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(ai.router, prefix="/ai", tags=["ai"])
