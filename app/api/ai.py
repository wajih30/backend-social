from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from app.api.deps import get_current_user
from app.models.user import User
from app.services.ai_service import get_ai_service

router = APIRouter()


class BioGenerateRequest(BaseModel):
    keywords: str


class BioGenerateResponse(BaseModel):
    suggestions: List[str]


@router.post("/generate-bio", response_model=BioGenerateResponse)
def generate_bio(
    request: BioGenerateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate AI-powered bio suggestions based on user keywords.
    
    Example keywords: "photographer, traveler, coffee lover"
    Returns 3 creative bio suggestions.
    """
    ai_service = get_ai_service()
    suggestions = ai_service.generate_bio_suggestions(request.keywords)
    
    return BioGenerateResponse(suggestions=suggestions)
