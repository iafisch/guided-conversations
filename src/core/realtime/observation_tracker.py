from typing import Dict, List, Set
from collections import defaultdict

class ObservationTracker:
    def __init__(self):
        self.observations: Dict[str, List[str]] = defaultdict(list)
        self.success_criteria: Dict[str, Set[str]] = defaultdict(set)
    
    def add_observation(self, phase: str, observation: str):
        self.observations[phase].append(observation)
    
    def criteria_met(self, phase: str, criterion: str):
        self.success_criteria[phase].add(criterion) 