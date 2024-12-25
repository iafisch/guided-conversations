from typing import Dict, List, Optional, Any
from pydantic import BaseModel

class ConversationPhase(BaseModel):
    name: str
    instructions: str
    success_criteria: List[str]
    required_observations: List[str]
    next_phases: List[str]
    max_duration_seconds: Optional[int]
    completion_rules: Dict[str, Any]  # Add logic later on how completion_rules are used

    class Config:
        extra = "forbid"


class ConversationConfig(BaseModel):
    name: str
    goal: str
    initial_phase: str
    system_instructions: str
    phases: Dict[str, ConversationPhase]
    max_duration_seconds: Optional[int]
    completion_criteria: Dict[str, Any]
    voice: str = "alloy"

    class Config:
        extra = "forbid" 