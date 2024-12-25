from fastapi import FastAPI, BackgroundTasks
from .routes import sessions, websocket

app = FastAPI()

# Include the routes from sessions.py
app.include_router(sessions.router, prefix="/conversations", tags=["conversations"])

# The WebSocket route is typically defined as an @app.websocket in websocket.py
# That is included below for clarity, but we won't "include_router" for websockets.

@app.get("/")
async def root():
    return {"message": "Guided Conversation Framework API"} 