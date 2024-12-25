from fastapi import Request, HTTPException
from typing import Optional
import os

async def verify_api_key(request: Request) -> Optional[str]:
    """Simple API key verification"""
    api_key = request.headers.get("Authorization")
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key")
    
    # In production, you'd want to use a proper key verification system
    expected_key = os.getenv("API_KEY", "development-key")
    if api_key != f"Bearer {expected_key}":
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return api_key 