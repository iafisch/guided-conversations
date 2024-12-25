import openai
import asyncio
import websockets
from typing import Optional, Dict
import time

from ...core.config.models import ConversationConfig
from ...conversation.tools import conversation_tool
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
    Manages a single Realtime AI conversation session, including creation of
    the OpenAI Realtime session and initialization of audio/event handlers.
    """
    def __init__(self, config: ConversationConfig):
        self.config = config
        self.state = SessionState()
        self.event_handler = RealtimeEventHandler(self)
        self.audio_processor = RealtimeAudioProcessor()
        self.phase_manager = PhaseManager(self)
        self.observation_tracker = ObservationTracker()
        self.conversation_tool = conversation_tool
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
                model="gpt-4-realtime",
                stream=True,
                voice=self.config.voice,
                audio_settings={
                    "sample_rate": 24000,
                    "audio_format": "pcm16",
                    "channels": 1
                },
                tools=[self.conversation_tool]
            )
            self.id = session.id
            self.token = session.token
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