# backend/services/flipped_interaction_service.py

class FlippedInteractionService:
    """
    Implements the Flipped Interaction Pattern where the system asks
    the user questions to understand their needs before giving answers.
    """

    def begin_interaction(self, user_input: str) -> dict:
        return {
            "system_question": "Thank you for sharing. What emotion do you feel most strongly right now?",
            "received_input": user_input
        }
