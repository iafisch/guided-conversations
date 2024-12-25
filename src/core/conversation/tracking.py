from typing import Dict, List, Optional, Set
from datetime import datetime
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class PhaseCompletion:
    """Records the completion details of a conversation phase"""
    phase: str
    duration_seconds: float
    success_criteria_met: Set[str]
    observations: List[Dict]
    completed_at: str


class ConversationTracker:
    """
    Tracks the overall progress and state of a conversation across all phases.
    This includes observations, success criteria, and completion status.
    """
    def __init__(self):
        self.phase_history: List[PhaseCompletion] = []
        self.observations: Dict[str, List[Dict]] = defaultdict(list)
        self.success_criteria: Dict[str, Set[str]] = defaultdict(set)
        self.start_time: float = datetime.utcnow().timestamp()
        
    def add_phase_completion(self, completion: PhaseCompletion):
        """Record the completion of a conversation phase"""
        self.phase_history.append(completion)
        
    def add_observation(self, phase: str, observation: str):
        """Add a new observation for the specified phase"""
        self.observations[phase].append({
            "observation": observation,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    def mark_criteria_met(self, phase: str, criterion: str):
        """Mark a success criterion as met for the specified phase"""
        self.success_criteria[phase].add(criterion)
        
    def get_phase_observations(self, phase: str) -> List[Dict]:
        """Get all observations for a specific phase"""
        return self.observations.get(phase, [])
        
    def get_met_criteria(self, phase: str) -> Set[str]:
        """Get all success criteria that have been met for a phase"""
        return self.success_criteria.get(phase, set())
        
    def get_conversation_duration(self) -> float:
        """Get the total duration of the conversation in seconds"""
        return datetime.utcnow().timestamp() - self.start_time
        
    def get_completion_status(self) -> Dict:
        """
        Get the overall completion status of the conversation,
        including phase history and success criteria
        """
        return {
            "duration_seconds": self.get_conversation_duration(),
            "phases_completed": len(self.phase_history),
            "total_observations": sum(len(obs) for obs in self.observations.values()),
            "success_criteria_met": {
                phase: list(criteria)
                for phase, criteria in self.success_criteria.items()
            },
            "phase_history": self.phase_history
        } 