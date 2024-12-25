from fastapi import APIRouter, BackgroundTasks
from typing import Dict
import uuid

from ...core.config.models import ConversationConfig
from ...core.realtime.session import RealtimeSession

router = APIRouter()

# Simple in-memory store for sessions
SESSIONS: Dict[str, RealtimeSession] = {}

@router.post("/")
async def create_conversation(config: ConversationConfig, background_tasks: BackgroundTasks):
    """
    Create a new guided conversation session using the provided ConversationConfig.
    Returns session_id and token for the client to use.
    """
    session_id = str(uuid.uuid4())
    session = RealtimeSession(config)
    
    # Initialize the Realtime session
    await session.initialize()

    # Keep track
    session.id = session_id
    SESSIONS[session_id] = session
    
    return {
        "session_id": session_id,
        "token": session.token
    }

def get_session(session_id: str) -> RealtimeSession:
    """
    Utility to retrieve a RealtimeSession from the store.
    """
    return SESSIONS.get(session_id) 