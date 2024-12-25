from fastapi import WebSocket, WebSocketDisconnect, HTTPException
import json
from typing import Optional
from src.api.routes.session_manager import get_session

async def realtime_endpoint(websocket: WebSocket, session_id: str):
    """
    Handle WebSocket connections for realtime audio streaming.
    
    This endpoint:
    - Validates the session
    - Processes incoming audio chunks
    - Handles text-based control messages
    - Manages WebSocket lifecycle
    
    Args:
        websocket: FastAPI WebSocket connection
        session_id: Unique identifier for the conversation session
        
    Raises:
        WebSocketDisconnect: When client disconnects
    """
    session = get_session(session_id)
    if not session:
        await websocket.close(code=4000)
        return
        
    await websocket.accept()
    
    try:
        while True:
            message = await websocket.receive()
            message_type = message.get("type")
            
            if message_type == "websocket.receive.bytes":
                audio_data = message.get("bytes")
                processed = await session.audio_processor.process_chunk(audio_data)
                if processed and session.ws:
                    await session.ws.send_bytes(processed)
            
            elif message_type == "websocket.receive.text":
                data = json.loads(message.get("text"))
                if data.get("type") == "end":
                    break
                await session.event_handler.handle_event(data)
                
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        print(f"Error in WebSocket handler: {e}")
    finally:
        # Cleanup
        if session.ws:
            await session.ws.close()