from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import Dict, Optional
import uuid
import asyncio
import json
from datetime import datetime, timedelta

from ...core.config.models import ConversationConfig
from ...core.realtime.session import RealtimeSession
from ...core.utils.errors import SessionError, handle_realtime_error

router = APIRouter()

# Simple in-memory store for sessions
SESSIONS: Dict[str, RealtimeSession] = {}

@router.post("/")
async def create_conversation(config: ConversationConfig, background_tasks: BackgroundTasks):
    """Create a new guided conversation session"""
    try:
        session_id = str(uuid.uuid4())
        session = RealtimeSession(config)
        
        # Initialize the Realtime session
        await session.initialize()
        
        if not session.id or not session.token:
            raise HTTPException(status_code=500, detail="Failed to initialize OpenAI session")

        # Store session
        session.id = session_id
        SESSIONS[session_id] = session
        
        # Add cleanup task
        background_tasks.add_task(cleanup_session, session_id)
        
        return {
            "session_id": session_id,
            "token": session.token
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{session_id}")
async def end_conversation(session_id: str):
    """Explicitly end a conversation session"""
    session = get_session(session_id)
    if session:
        await cleanup_session(session_id)
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="Session not found")

def get_session(session_id: str) -> RealtimeSession:
    """Get a session by ID"""
    return SESSIONS.get(session_id)

async def cleanup_session(session_id: str, delay: int = 3600):
    """Clean up session after delay (default 1 hour) or when explicitly ended"""
    try:
        await asyncio.sleep(delay)
    finally:
        if session_id in SESSIONS:
            session = SESSIONS[session_id]
            if session.ws:
                await session.ws.close()
            del SESSIONS[session_id] 