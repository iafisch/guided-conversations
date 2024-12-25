from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel
import time

from ...core.config.models import ConversationConfig
from ..realtime.session import RealtimeSession

class PhaseCompletion(BaseModel):
    phase: str
    duration_seconds: Optional[float] = 0.0
    success_criteria_met: List[str] = []
    observations: List[str] = []
    completed_at: Optional[str] = None


class PhaseManager:
    """Manages conversation phases and transitions."""
    
    def __init__(self, session: RealtimeSession):
        self.session = session
        self.config: ConversationConfig = session.config
        self.current_phase = self.config.initial_phase
        self.phase_history: List[PhaseCompletion] = []
        self.phase_start_time = datetime.utcnow()

    async def transition_phase(self, new_phase: str) -> bool:
        """
        Handle phase transitions:
         - Validate that 'new_phase' is in the current phase’s next_phases list.
         - Record completion metrics.
         - Update the current phase.
         - Optionally instruct the AI to update system instructions accordingly.
        """
        current_phase_def = self.config.phases[self.current_phase]

        # Validate transition
        if new_phase not in current_phase_def.next_phases:
            return False

        # Record completion metrics for the old/current phase
        now = datetime.utcnow()
        duration_seconds = (now - self.phase_start_time).total_seconds()
        completed_phase = PhaseCompletion(
            phase=self.current_phase,
            duration_seconds=duration_seconds,
            success_criteria_met=self._get_met_criteria(self.current_phase),
            observations=self._get_phase_observations(self.current_phase),
            completed_at=now.isoformat()
        )
        self.phase_history.append(completed_phase)

        # Update current phase
        self.current_phase = new_phase
        self.phase_start_time = now  # reset timer for new phase

        # Optionally tell the AI to adjust instructions for new phase
        await self._update_instructions()

        return True

    def _get_met_criteria(self, phase: str) -> List[str]:
        """
        Retrieve success criteria that have been met for a given phase,
        from the session’s observation or tracking system if available.
        """
        # This might integrate with an ObservationTracker instance
        # For now, we do a placeholder return:
        return []

    def _get_phase_observations(self, phase: str) -> List[str]:
        """
        Retrieve observations recorded for a given phase.
        """
        # For now, a placeholder
        return []

    def get_phase_duration(self) -> float:
        """Get duration of current phase in seconds"""
        if self.session.state.phase_start_time is None:
            return 0.0
        return time.time() - self.session.state.phase_start_time
        
    def get_met_criteria(self) -> List[str]:
        """Get list of met success criteria for current phase"""
        return list(self.session.observation_tracker.success_criteria[self.current_phase])
        
    def get_phase_observations(self) -> List[Dict]:
        """Get observations for current phase"""
        return self.session.observation_tracker.observations[self.current_phase]

    async def _update_instructions(self):
        """Update system instructions for new phase"""
        phase_config = self.session.config.phases[self.current_phase]
        instructions = f"{self.session.config.system_instructions}\n\nCurrent phase: {phase_config.name}\n{phase_config.instructions}"
        
        # Update session instructions via API
        await self.session.ws.send_json({
            "type": "update_instructions",
            "instructions": instructions
        }) 