from src.core.config.models import ConversationConfig, ConversationPhase

restaurant_ordering_config = ConversationConfig(
    name="AI Waiter",
    goal="Guide a customer through a complete restaurant ordering process, including drinks, appetizers, main courses, and upsell opportunities",
    initial_phase="greeting",
    system_instructions="""
You are a friendly and attentive waiter. Provide menu options, gather the
customer's preferences, and confirm their final order. Make helpful
suggestions where appropriate.
""",
    phases={
        "greeting": ConversationPhase(
            name="Greeting",
            instructions="Welcome the customer, confirm party size, and seating preferences.",
            success_criteria=["greeting_complete"],
            required_observations=["party_size", "seating_preferences"],
            next_phases=["drinks_order"],
            max_duration_seconds=120,
            completion_rules={}
        ),
        "drinks_order": ConversationPhase(
            name="Drinks Order",
            instructions="Offer drink options, gather preferences (e.g., alcoholic, non-alcoholic, or specialty). Note any allergies or restrictions.",
            success_criteria=["drinks_completed"],
            required_observations=["drink_preferences"],
            next_phases=["appetizer_order"],
            max_duration_seconds=180,
            completion_rules={}
        ),
        "appetizer_order": ConversationPhase(
            name="Appetizer Order",
            instructions="Offer appetizer options. Take the order and suggest house specialties if they haven't chosen yet.",
            success_criteria=["appetizers_noted"],
            required_observations=["appetizer_choices"],
            next_phases=["main_order"],
            max_duration_seconds=180,
            completion_rules={}
        ),
        "main_order": ConversationPhase(
            name="Main Order",
            instructions="Discuss main courses. Confirm any dietary restrictions or preferences. Upsell sides if appropriate.",
            success_criteria=["main_course_selected"],
            required_observations=["main_preferences"],
            next_phases=["order_confirmation"],
            max_duration_seconds=300,
            completion_rules={}
        ),
        "order_confirmation": ConversationPhase(
            name="Order Confirmation",
            instructions="Read back the entire order (drinks, appetizers, mains). Confirm correctness and ask if there's anything else needed.",
            success_criteria=["order_confirmed"],
            required_observations=["final_order_check"],
            next_phases=["conclusion"],
            max_duration_seconds=120,
            completion_rules={}
        ),
        "conclusion": ConversationPhase(
            name="Conclusion",
            instructions="Thank the customer and let them know their order is being prepared.",
            success_criteria=["parting_statement"],
            required_observations=["customer_acknowledgment"],
            next_phases=[],
            max_duration_seconds=60,
            completion_rules={}
        )
    },
    max_duration_seconds=1800,  # Entire conversation limit
    completion_criteria={
        "global": "Order is complete after final confirmation and conclusion."
    },
    voice="alloy"
)
