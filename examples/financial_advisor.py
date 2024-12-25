from src.core.config.models import ConversationConfig, ConversationPhase

financial_advisor_config = ConversationConfig(
    name="Financial Advisory Session",
    goal="Provide personal finance advice, clarify risk tolerance, and make recommendations",
    initial_phase="introduction",
    system_instructions="""
You are a seasoned financial advisor. Greet the client, inquire about
their investment goals, clarify their risk tolerance, and conclude with
tailored recommendations.
""",
    phases={
        "introduction": ConversationPhase(
            name="Introduction",
            instructions="Welcome the client, explain the scope of the session, and gather basic financial goals.",
            success_criteria=["introduction_complete"],
            required_observations=["initial_goals"],
            next_phases=["risk_assessment"],
            max_duration_seconds=120,
            completion_rules={}
        ),
        "risk_assessment": ConversationPhase(
            name="Risk Assessment",
            instructions="Ask questions to determine the client's risk tolerance, investment horizon, and liquidity needs.",
            success_criteria=["risk_profile_determined"],
            required_observations=["risk_tolerance", "investment_horizon"],
            next_phases=["recommendations"],
            max_duration_seconds=300,
            completion_rules={}
        ),
        "recommendations": ConversationPhase(
            name="Recommendations",
            instructions="Provide suggestions for investment instruments or savings plans based on the risk profile. Note any relevant disclaimers or disclaim that it's not official legal advice.",
            success_criteria=["recommendations_provided"],
            required_observations=["client_reactions"],
            next_phases=["conclusion"],
            max_duration_seconds=300,
            completion_rules={}
        ),
        "conclusion": ConversationPhase(
            name="Conclusion",
            instructions="Summarize the recommended strategy, confirm client understanding, and wrap up.",
            success_criteria=["wrapup_acknowledged"],
            required_observations=["client_acknowledgment"],
            next_phases=[],
            max_duration_seconds=120,
            completion_rules={}
        )
    },
    max_duration_seconds=1200,  # Entire conversation limit
    completion_criteria={
        "global": "Session concludes after recommendations are provided and acknowledged."
    },
    voice="alloy"
) 