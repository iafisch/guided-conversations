# src/api/routes/session_manager.py
from fastapi import APIRouter, HTTPException
from typing import Dict
import uuid
import asyncio

from src.core.realtime.session import RealtimeSession
from src.core.config.models import ConversationConfig

router = APIRouter()
SESSIONS: Dict[str, RealtimeSession] = {}

@router.post("/")
async def create_session(config: ConversationConfig):
    session_id = str(uuid.uuid4())
    session = RealtimeSession(config)
    await session.initialize()
    SESSIONS[session_id] = session
    return {"session_id": session_id}

def get_session(session_id: str) -> RealtimeSession:
    return SESSIONS.get(session_id)