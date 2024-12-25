from src.core.config.models import ConversationConfig, ConversationPhase

basic_config = ConversationConfig(
    name="Basic Conversation",
    goal="Have a simple conversation with phase transitions",
    initial_phase="greeting",
    system_instructions="""You are a helpful assistant. Guide the conversation 
    through the phases naturally, using the conversation tool to track progress.""",
    phases={
        "greeting": ConversationPhase(
            name="Greeting",
            instructions="Welcome the user and introduce yourself",
            success_criteria=["user_greeted"],
            required_observations=["user_response"],
            next_phases=["main_conversation"]
        ),
        "main_conversation": ConversationPhase(
            name="Main Conversation",
            instructions="Engage in conversation, ask about their needs",
            success_criteria=["needs_identified"],
            required_observations=["user_needs"],
            next_phases=["conclusion"]
        ),
        "conclusion": ConversationPhase(
            name="Conclusion",
            instructions="Wrap up the conversation politely",
            success_criteria=["farewell_given"],
            required_observations=["user_farewell"],
            next_phases=[]
        )
    },
    voice="alloy"
) 