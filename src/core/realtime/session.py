import os
import json
import time
import asyncio
import aiohttp  # For async HTTP requests
import websockets
from typing import Optional, Dict

from ...core.config.models import ConversationConfig
from .events import RealtimeEventHandler
from .audio import RealtimeAudioProcessor
from .phase_manager import PhaseManager
from .observation_tracker import ObservationTracker


class SessionState:
    """
    Tracks the state of the conversation session. This is minimal for now;
    we can expand it with more attributes (e.g. current phase, timestamps, etc.)
    as needed.
    """
    def __init__(self):
        self.active: bool = False
        self.current_phase: Optional[str] = None
        self.phase_start_time: Optional[float] = None
        self.conversation_start_time: float = time.time()
        self.completion_status: Dict[str, bool] = {}


class RealtimeSession:
    """
    Manages a single Realtime AI conversation session.
    
    This class handles:
    - OpenAI Realtime session creation and management
    - WebSocket connection setup and maintenance
    - Audio processing initialization
    - Event handling coordination
    - Phase management
    - Observation tracking
    
    Attributes:
        config (ConversationConfig): Configuration for the conversation
        state (SessionState): Current state of the session
        event_handler (RealtimeEventHandler): Handles incoming events
        audio_processor (RealtimeAudioProcessor): Processes audio chunks
        phase_manager (PhaseManager): Manages conversation phases
        observation_tracker (ObservationTracker): Tracks observations and criteria
        ws (websockets.WebSocketClientProtocol): WebSocket connection to OpenAI
    """
    def __init__(self, config: ConversationConfig):
        self.config = config
        self.state = SessionState()
        self.event_handler = RealtimeEventHandler(self)
        self.audio_processor = RealtimeAudioProcessor()
        self.phase_manager = PhaseManager(self)
        self.observation_tracker = ObservationTracker()
        # We'll assume openai.api_key is set externally for your environment:
        self.api_key = os.environ.get("OPENAI_API_KEY", "")
        self.ws = None
        
        # Session identifiers populated after create() call
        self.id: Optional[str] = None
        self.token: Optional[str] = None

    async def initialize(self):
        """
        Creates the OpenAI Realtime session and sets up the WebSocket connection.
        """
        try:
            # 1. Create the session via HTTP POST
            session_data = await self._create_realtime_session()

            # 2. Store session details
            self.id = session_data["id"]
            self.token = session_data["client_secret"]["value"]

            # 3. Connect to WebSocket using the ephemeral token
            await self._setup_websocket(token=self.token)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize realtime session: {e}")

    async def _create_realtime_session(self) -> Dict:
        """
        Calls POST https://api.openai.com/v1/realtime/sessions to create a session.
        Returns the JSON of the created session, e.g.:
        {
          "id": "sess_001",
          "object": "realtime.session",
          ...
          "client_secret": {"value": "...", ...}
        }
        """
        url = "https://api.openai.com/v1/realtime/sessions"
        
        # Build the request JSON according to the Beta docs
        # (You can adapt or add fields if needed, e.g. modalities, tools, etc.)
        body = {
            "model": "gpt-4o-realtime-preview-2024-12-17",
            "modalities": ["audio", "text"],
            "voice": self.config.voice,
            "instructions": self._build_instructions(),
            "tools": [self.conversation_tool_definition()]
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "OpenAI-Beta": "realtime=v1",
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=body) as resp:
                if resp.status != 200:
                    text_error = await resp.text()
                    raise RuntimeError(
                        f"Failed to create Realtime session: {resp.status} {text_error}"
                    )
                return await resp.json()

    def _build_instructions(self) -> str:
        """
        Merges or transforms the system instructions from the config
        if necessary. For now, it simply returns the raw instructions
        defined in the config.
        """
        return self.config.system_instructions or ""

    def conversation_tool_definition(self) -> Dict:
        """
        Build a single tool (function) definition for the Realtime session creation.
        In the new Realtime Beta, each tool is an object in a 'tools' array.
        For example:
          {
            "type": "function",
            "name": "conversation_tool",
            "description": "Handles conversation tool calls from the AI",
            "parameters_schema": {...}
          }
        """
        return {
            "type": "function",
            "name": "conversation_tool",
            "description": "Handle conversation tool function calls from the AI",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["observe", "transition", "complete"]
                    },
                    "observations": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "transition_to": {"type": "string"},
                    "completion_notes": {"type": "string"}
                },
                "required": ["action"]
            }
        }

    async def _setup_websocket(self, token: str):
        """
        Connect to wss://api.openai.com/v1/realtime
        using the API key.
        """
        ws_url = "wss://api.openai.com/v1/realtime"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "OpenAI-Beta": "realtime=v1"
        }
        
        try:
            self.ws = await websockets.connect(
                ws_url, 
                additional_headers=headers,
                ping_interval=20,
                ping_timeout=20
            )
            print(f"[info] WebSocket connected for session {self.id}")
            
            # Send initial session update matching the API's structure
            update_message = {
                "type": "session.update",
                "session": {
                    "model": "gpt-4o-realtime-preview-2024-12-17",
                    "modalities": ["audio", "text"],
                    "voice": self.config.voice,
                    "instructions": self._build_instructions(),
                    "tools": [self.conversation_tool_definition()],
                    "input_audio_format": "pcm16",
                    "output_audio_format": "pcm16"
                }
            }
            await self.ws.send(json.dumps(update_message))
            print("[debug] Sent session update message")
            
            # Then send audio format confirmation
            audio_config = {
                "type": "input_audio_buffer.append",
                "format": "pcm16",
                "sample_rate": 24000,
                "channels": 1
            }
            await self.ws.send(json.dumps(audio_config))
            print("[debug] Sent audio format config")
            
        except Exception as e:
            print(f"[error] Failed to connect to WebSocket: {e}")
            self.ws = None

    async def conversation_tool(self, args: Dict) -> Dict:
        """
        Handle conversation tool function calls from the AI.
        If the model calls `conversation_tool` with arguments like:
        {
           "action": "observe",
           "observations": [...]
        }
        we do the relevant internal updates.
        """
        response = {"status": "success"}
        action = args.get("action")
        
        if action == "observe":
            observations = args.get("observations", [])
            for obs in observations:
                self.observation_tracker.add_observation(
                    self.phase_manager.current_phase,
                    obs
                )
            response["observations_added"] = len(observations)
            
        elif action == "transition":
            new_phase = args.get("transition_to")
            if new_phase:
                success = await self.phase_manager.transition_phase(new_phase)
                response["transition_success"] = success
                
        elif action == "complete":
            completion_notes = args.get("completion_notes")
            self.state.completion_status["completed"] = True
            self.state.completion_status["notes"] = completion_notes
            
        return response