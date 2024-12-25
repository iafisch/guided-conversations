import openai
import asyncio
import websockets
from typing import Optional, Dict
import time

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
        self.client = openai  # Assumes openai.api_key is set externally
        self.ws = None
        
        # Session identifiers populated after create() call
        self.id: Optional[str] = None
        self.token: Optional[str] = None

    async def initialize(self):
        """
        Creates the OpenAI Realtime session and sets up the WebSocket connection.
        """
        try:
            session = await self.client.audio.realtime.sessions.create(
                model="gpt-4-turbo-preview",
                voice=self.config.voice,
                instructions=self._build_instructions(),
                tools=[self.conversation_tool],
                input_audio_format="pcm16",
                input_audio_settings={
                    "sample_rate": 24000,
                    "channels": 1
                },
                output_audio_format="pcm16",
                output_audio_settings={
                    "sample_rate": 24000,
                    "channels": 1
                }
            )
            self.id = session.id
            self.token = session.client_secret.value
            await self._setup_websocket(self.token)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize realtime session: {e}")

    def _build_instructions(self) -> str:
        """
        Merges or transforms the system instructions from the config
        if necessary. For now, it simply returns the raw instructions
        defined in the config.
        """
        return self.config.system_instructions

    async def _setup_websocket(self, client_secret: str):
        """Real OpenAI WebSocket connection"""
        ws_url = f"wss://realtime.openai.com/v1/audio/sessions/{self.id}"
        try:
            self.ws = await websockets.connect(
                ws_url,
                extra_headers={
                    "Authorization": f"Bearer {client_secret}",
                    "OpenAI-Organization": self.client.organization  # Add org ID if available
                }
            )
        except Exception as e:
            print(f"[error] Failed to connect to WebSocket: {e}")
            self.ws = None 

    async def conversation_tool(self, args: Dict) -> Dict:
        """Handle conversation tool function calls from the AI."""
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