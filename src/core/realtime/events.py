from typing import Dict
import json

class RealtimeEventHandler:
    """
    Handles all Realtime API events, dispatching to specific handler methods 
    based on the event's type field.
    """

    def __init__(self, session):
        """
        session: An instance of RealtimeSession.
        """
        self.session = session

    async def handle_event(self, event: Dict):
        event_type = event.get("type")
        
        # Map of event_type -> handler function
        handlers = {
            # Session events
            "session.created": self._handle_session_created,
            "session.updated": self._handle_session_updated,

            # Conversation events
            "conversation.created": self._handle_conversation_created,
            "conversation.item.created": self._handle_item_created,

            # Response events
            "response.created": self._handle_response_created,
            "response.done": self._handle_response_done,

            # Content events
            "response.text.delta": self._handle_text_delta,
            "response.audio.delta": self._handle_audio_delta,

            # Function calling events
            "response.function_call_arguments.delta": self._handle_function_call_delta,
            "response.function_call_arguments.done": self._handle_function_call_done,

            # Audio buffer events
            "input_audio_buffer.speech_started": self._handle_speech_started,
            "input_audio_buffer.speech_stopped": self._handle_speech_stopped,

            # Add missing handlers from docs
            "response.audio_transcript.delta": self._handle_audio_transcript_delta,
            "response.audio_transcript.done": self._handle_audio_transcript_done,
            "rate_limits.updated": self._handle_rate_limits_updated,
        }

        handler = handlers.get(event_type)
        if handler is not None:
            await handler(event)
        else:
            # Optionally handle unknown events
            pass

    async def _handle_session_created(self, event: Dict):
        """
        Handle session.created event. This might update session state 
        or do any initialization logic needed after a new session is created.
        """
        # Example:
        self.session.state.active = True

    async def _handle_session_updated(self, event: Dict):
        """Handle session.updated event."""
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
        """Handle response.text.delta event."""
        pass

    async def _handle_audio_delta(self, event: Dict):
        """Handle response.audio.delta event."""
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