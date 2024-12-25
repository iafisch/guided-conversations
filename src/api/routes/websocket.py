from fastapi import WebSocket, WebSocketDisconnect
from .sessions import get_session

async def realtime_endpoint(websocket: WebSocket, session_id: str):
    """
    Handle WebSocket connection for real-time audio + text interaction.
    """
    session = get_session(session_id)
    if not session:
        await websocket.close(code=4000, reason="Invalid session")
        return

    # Accept the connection
    await websocket.accept()

    try:
        # Basic loop to receive messages (audio chunks, commands, etc.)
        while True:
            data = await websocket.receive_bytes()
            # For demonstration, assume all inbound data is an audio chunk
            # You might add logic to handle JSON messages (e.g., end_session, get_status)
            processed_chunk = await session.audio_processor.process_chunk(data)
            if processed_chunk is not None:
                # Potentially forward to the OpenAI Realtime API
                # Or handle local logic
                pass

    except WebSocketDisconnect:
        # Client disconnected
        await websocket.close()
    except Exception as e:
        # On error, close with a relevant code or log it
        await websocket.close(code=1011, reason=str(e)) 