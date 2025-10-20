"""
User Preferences Router
Manages user preferences for tools/parts display
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID
from api.config.db import get_db

router = APIRouter(prefix="/user-preferences", tags=["user-preferences"])

# In-memory storage for now (in production, this would be in database)
user_preferences_store = {}

@router.get("/tools-parts")
def get_tools_parts_preference(
    user_id: UUID = Query(..., description="UUID of the user"),
    db: Session = Depends(get_db)
):
    """Get user preference for showing tools and parts information."""
    
    # Default to True (show tools/parts) for new users
    preference = user_preferences_store.get(str(user_id), True)
    
    return {
        "user_id": user_id,
        "show_tools_parts": preference,
        "description": "Whether to show tools and parts information in LLM responses"
    }

@router.post("/tools-parts")
def set_tools_parts_preference(
    user_id: UUID = Query(..., description="UUID of the user"),
    show_tools_parts: bool = Query(..., description="Whether to show tools/parts information"),
    db: Session = Depends(get_db)
):
    """Set user preference for showing tools and parts information."""
    
    user_preferences_store[str(user_id)] = show_tools_parts
    
    return {
        "user_id": user_id,
        "show_tools_parts": show_tools_parts,
        "updated": True,
        "message": f"Tools/parts display {'enabled' if show_tools_parts else 'disabled'}"
    }