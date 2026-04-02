# backend/routes/flipped_routes.py

from fastapi import APIRouter
from backend.services.flipped_interaction_service import FlippedInteractionService
from backend.config.feature_flags import FEATURE_FLAGS

router = APIRouter()
flipped_service = FlippedInteractionService()


@router.post("/start")
async def start_flipped_interaction(user_input: str):
    """
    Begin flipped-interaction pattern with the user.
    """

    # Feature flag guard
    if not FEATURE_FLAGS.get("ENABLE_FLIPPED_INTERACTION", True):
        return {
            "message": "Flipped interaction is currently disabled."
        }

    return flipped_service.start_interaction(user_input)
