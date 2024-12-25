from typing import Optional

class ConversationError(Exception):
    """Base error for conversation-related issues"""
    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class SessionError(ConversationError):
    """Errors related to session management"""
    pass

class AudioError(ConversationError):
    """Errors related to audio processing"""
    pass

class WebSocketError(ConversationError):
    """Errors related to WebSocket communication"""
    pass

def handle_realtime_error(error: Exception) -> ConversationError:
    """Convert various errors to ConversationError types"""
    if isinstance(error, (ConnectionError, TimeoutError)):
        return WebSocketError(
            "Connection to OpenAI Realtime API failed",
            {"original_error": str(error)}
        )
    return ConversationError(
        "Unexpected error occurred",
        {"error_type": type(error).__name__, "details": str(error)}
    ) 