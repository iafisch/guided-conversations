from typing import Dict, List, Optional
from ...core.realtime.session import RealtimeSession

async def handle_conversation_tool(session: "RealtimeSession", args: Dict) -> Dict:
    """Handle conversation tool function calls"""
    action = args.get("action")
    response = {"success": True}
    
    if action == "observe":
        observations = args.get("observations", [])
        for obs in observations:
            session.observation_tracker.add_observation(
                session.phase_manager.current_phase,
                obs
            )
        response["observations_added"] = len(observations)
        
    elif action == "transition":
        new_phase = args.get("transition_to")
        if new_phase:
            success = await session.phase_manager.transition_phase(new_phase)
            response["transition_success"] = success
            
    elif action == "complete":
        completion_notes = args.get("completion_notes")
        session.state.completion_status["completed"] = True
        session.state.completion_status["notes"] = completion_notes
        
    return response

conversation_tool = {
    "name": "conversation_tool",
    "description": "Manages conversation flow and state",
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["observe", "transition", "complete"]
            },
            "observations": {
                "type": "array",
                "items": {"type": "string"}
            },
            "success_criteria_met": {
                "type": "array",
                "items": {"type": "string"}
            },
            "transition_to": {"type": "string"},
            "completion_notes": {"type": "string"}
        },
        "required": ["action"]
    }
} 