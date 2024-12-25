from typing import Dict, Optional
import json
from datetime import datetime
from ..utils.errors import handle_realtime_error

class RealtimeEventHandler:
    """Handles all Realtime API events"""
    
    def __init__(self, session):
        """Initialize the event handler with a session reference.
        
        Args:
            session: The RealtimeSession instance this handler is associated with
        """
        self.session = session
    
    async def handle_event(self, event: Dict):
        """Handle incoming events from the Realtime API"""
        print(f"[debug] Received event: {json.dumps(event, indent=2)}")  # Debug line
        
        event_type = event.get("type", "")
        
        handlers = {
            "session.created": self._handle_session_created,
            "error": self._handle_error,
            "text.delta": self._handle_text_delta,
            "text.done": self._handle_text_done,
            "audio.delta": self._handle_audio_delta,
            "audio.done": self._handle_audio_done,
            "audio_transcript.delta": self._handle_audio_transcript_delta,
            "audio_transcript.done": self._handle_audio_transcript_done,
            "function_call.delta": self._handle_function_call_delta,
            "function_call.done": self._handle_function_call_done,
            "speech.started": self._handle_speech_started,
            "speech.stopped": self._handle_speech_stopped
        }
        
        handler = handlers.get(event_type)
        if handler:
            await handler(event)
        else:
            print(f"[warning] Unhandled event type: {event_type}")
            print(f"[debug] Event data: {json.dumps(event, indent=2)}")

    async def _handle_session_created(self, event: Dict):
        """
        Handle session.created event. This might update session state 
        or do any initialization logic needed after a new session is created.
        """
        # Example:
        self.session.state.active = True

    async def _handle_session_updated(self, event: Dict):
        """Handle session.updated event properly"""
        print("[debug] Session updated successfully")
        # Update any local state if needed
        pass

    async def _handle_conversation_created(self, event: Dict):
        """Handle conversation.created event."""
        pass

    async def _handle_item_created(self, event: Dict):
        """Handle conversation.item.created event."""
        pass

    async def _handle_response_created(self, event: Dict):
        """Handle response.created event."""
        pass

    async def _handle_response_done(self, event: Dict):
        """Handle response.done event."""
        pass

    async def _handle_text_delta(self, event: Dict):
        """Handle text.delta event"""
        if "content" in event:
            print(event["content"], end="", flush=True)

    async def _handle_text_done(self, event: Dict):
        """Handle text.done event"""
        print("")  # New line after text completion

    async def _handle_audio_delta(self, event: Dict):
        """Handle audio.delta event"""
        pass

    async def _handle_audio_done(self, event: Dict):
        """Handle audio.done event"""
        pass

    async def _handle_audio_transcript_delta(self, event: Dict):
        """Handle audio_transcript.delta event"""
        if "content" in event:
            print(f"Transcript: {event['content']}")

    async def _handle_audio_transcript_done(self, event: Dict):
        """Handle audio_transcript.done event"""
        pass

    async def _handle_function_call_delta(self, event: Dict):
        """Handle function call arguments delta event"""
        if "content" in event:
            # Parse function call data
            try:
                data = json.loads(event["content"])
                if data.get("action") == "observe":
                    for observation in data.get("observations", []):
                        self.session.observation_tracker.add_observation(
                            self.session.phase_manager.current_phase,
                            observation
                        )
                elif data.get("action") == "transition":
                    new_phase = data.get("transition_to")
                    if new_phase:
                        await self.session.phase_manager.transition_phase(new_phase)
            except json.JSONDecodeError:
                pass

    async def _handle_function_call_done(self, event: Dict):
        """Handle function call completion"""
        # Check if phase completion criteria are met
        current_phase = self.session.phase_manager.current_phase
        phase_config = self.session.config.phases[current_phase]
        
        # Update success criteria
        if "success_criteria_met" in event:
            for criterion in event["success_criteria_met"]:
                self.session.observation_tracker.criteria_met(current_phase, criterion)

    async def _handle_speech_started(self, event: Dict):
        """Handle input_audio_buffer.speech_started event."""
        pass

    async def _handle_speech_stopped(self, event: Dict):
        """Handle input_audio_buffer.speech_stopped event."""
        pass

    async def _handle_error(self, event: Dict):
        """Handle error events from the API"""
        print(f"[error] API Error: {json.dumps(event, indent=2)}") 