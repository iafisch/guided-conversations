from typing import Optional
from ...core.config.models import ConversationConfig

class PhaseManager:
    """
    Manages conversation phase transitions and state.
    
    Handles:
    - Current phase tracking
    - Phase transitions
    - Phase completion validation
    - Duration tracking
    """
    
    def __init__(self, session):
        self.session = session
        self.current_phase = session.config.initial_phase
        self.session.state.current_phase = self.current_phase
        
    async def transition_phase(self, new_phase: str) -> bool:
        """
        Attempt to transition to a new conversation phase.
        
        Args:
            new_phase: Name of the phase to transition to
            
        Returns:
            bool: True if transition was successful
        """
        if new_phase not in self.session.config.phases:
            return False
            
        current_phase_config = self.session.config.phases[self.current_phase]
        if new_phase not in current_phase_config.next_phases:
            return False
            
        self.current_phase = new_phase
        self.session.state.current_phase = new_phase
        self.session.state.phase_start_time = self.session.state.conversation_start_time
        
        return True
        
    def get_current_phase_config(self):
        """Get the configuration for the current phase."""
        return self.session.config.phases[self.current_phase] 