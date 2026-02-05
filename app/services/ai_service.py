from typing import List
from groq import Groq
from fastapi import HTTPException, status
from app.core.config import settings


class GroqAIService:
    """Service for Groq AI interactions"""
    
    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not configured")
        
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"
    
    def generate_bio_suggestions(self, keywords: str, count: int = 3) -> List[str]:
        """
        Generate creative bio suggestions based on user keywords.
        
        Args:
            keywords: User-provided keywords (e.g., "photographer, traveler, coffee lover")
            count: Number of suggestions to generate
            
        Returns:
            List of bio suggestion strings
        """
        if not keywords or len(keywords.strip()) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please provide at least a few keywords to generate a bio."
            )
        
        try:
            prompt = f"""Generate {count} creative, engaging social media bios based on these keywords: {keywords}

Requirements:
- Each bio should be 1-2 sentences max (under 150 characters preferred)
- Make them catchy, professional, or witty
- Include relevant emojis
- Each bio should have a different tone (professional, casual, creative)

Return ONLY a JSON array of strings, no other text. Example format:
["Bio 1 here ✨", "Bio 2 here 🚀", "Bio 3 here 💡"]"""

            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8  # Higher for creativity
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            import json
            bios = json.loads(response_text)
            
            # Validate
            if not isinstance(bios, list):
                raise ValueError("Invalid response format")
            
            bios = [bio.strip() for bio in bios if isinstance(bio, str) and bio.strip()]
            
            return bios[:count]
            
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract bios manually
            return [f"✨ {keywords.title()} enthusiast"]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI bio generation failed: {str(e)}"
            )


# Singleton instance
_ai_service = None

def get_ai_service() -> GroqAIService:
    """Get or create the AI service singleton"""
    global _ai_service
    if _ai_service is None:
        _ai_service = GroqAIService()
    return _ai_service
