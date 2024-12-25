from typing import Dict, List, Set
from collections import defaultdict

class ObservationTracker:
    """Tracks observations and success criteria for conversation phases"""
    
    def __init__(self):
        self.observations: Dict[str, List[str]] = defaultdict(list)
        self.success_criteria: Dict[str, Set[str]] = defaultdict(set)
    
    def add_observation(self, phase: str, observation: str):
        """Add an observation for a specific phase"""
        self.observations[phase].append(observation)
    
    def criteria_met(self, phase: str, criterion: str):
        """Mark a success criterion as met for a specific phase"""
        self.success_criteria[phase].add(criterion)
    
    def get_completion_status(self) -> Dict:
        """Get the overall completion status including observations and criteria met"""
        total_observations = sum(len(obs) for obs in self.observations.values())
        phases_completed = []
        
        # A phase is considered complete if it has any success criteria met
        for phase in self.success_criteria:
            if len(self.success_criteria[phase]) > 0:
                phases_completed.append(phase)
        
        return {
            "total_observations": total_observations,
            "phases_completed": phases_completed,
            "duration_seconds": 0.0  # This could be calculated if we track timestamps
        } 