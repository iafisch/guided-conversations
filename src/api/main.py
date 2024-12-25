from fastapi import FastAPI, WebSocket, Depends
from fastapi.middleware.cors import CORSMiddleware
from .routes import sessions, websocket
from .middleware.auth import verify_api_key

app = FastAPI(
    title="Guided Conversation Framework",
    description="Framework for building multi-phase, AI-guided conversations",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routes
app.include_router(
    sessions.router,
    prefix="/conversations",
    tags=["conversations"],
    dependencies=[Depends(verify_api_key)]
)

@app.websocket("/realtime/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.realtime_endpoint(websocket, session_id)

@app.get("/")
async def root():
    return {
        "message": "Guided Conversation Framework API",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json"
    } 