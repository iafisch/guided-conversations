from src.core.config.models import ConversationConfig, ConversationPhase

language_assessment_config = ConversationConfig(
    name="Language Proficiency Assessment",
    goal="Assess the speaker's English language proficiency across grammar, vocabulary, fluency, and pronunciation",
    initial_phase="welcome",
    system_instructions="""
You are a professional language assessor. Guide the conversation naturally
while evaluating the speaker's language abilities, including grammar,
vocabulary, and fluency. Ensure you gather enough samples of their speech
to make an informed assessment.
""",
    phases={
        "welcome": ConversationPhase(
            name="Welcome",
            instructions="Greet and put the user at ease. Collect initial comfort level.",
            success_criteria=["comfort_established"],
            required_observations=["initial_comfort_level"],
            next_phases=["grammar_assessment"],
            max_duration_seconds=120,
            completion_rules={}
        ),
        "grammar_assessment": ConversationPhase(
            name="Grammar Assessment",
            instructions="Ask questions that prompt a variety of grammatical structures. Listen for accuracy in tense usage, subject-verb agreement, and sentence structure. Record grammar observations.",
            success_criteria=["grammar_evaluated"],
            required_observations=["grammar_accuracy"],
            next_phases=["vocabulary_assessment"],
            max_duration_seconds=300,
            completion_rules={}
        ),
        "vocabulary_assessment": ConversationPhase(
            name="Vocabulary Assessment",
            instructions="Engage the user in a short discussion to evaluate their range of vocabulary. Prompt for synonyms, descriptive words, etc. Record vocabulary richness.",
            success_criteria=["vocabulary_evaluated"],
            required_observations=["vocabulary_range"],
            next_phases=["fluency_assessment"],
            max_duration_seconds=300,
            completion_rules={}
        ),
        "fluency_assessment": ConversationPhase(
            name="Fluency Assessment",
            instructions="Prompt user for free-form speech on a familiar topic. Evaluate pace, hesitation, and coherence. Record fluency observations.",
            success_criteria=["fluency_evaluated"],
            required_observations=["fluency_score"],
            next_phases=["conclusion"],
            max_duration_seconds=300,
            completion_rules={}
        ),
        "conclusion": ConversationPhase(
            name="Conclusion",
            instructions="Provide an overall impression and wrap up. Optionally give recommendations for improvement.",
            success_criteria=["final_recommendations_provided"],
            required_observations=["overall_impression"],
            next_phases=[],
            max_duration_seconds=120,
            completion_rules={}
        )
    },
    max_duration_seconds=1200,  # Entire conversation limit
    completion_criteria={
        "global": "Assessment completed after final recommendations are provided."
    },
    voice="alloy"
) 