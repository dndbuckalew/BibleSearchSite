# backend/core/escalation/escalation_messages.py

from typing import Dict, Any


LEVEL_TO_MESSAGE: Dict[str, Dict[str, Any]] = {
    "hard_stop": {
        "level": "hard_stop",
        "title": "Safety boundary reached",
        "message": (
            "I can’t continue with this request. If you are in immediate danger, call your local emergency number now. "
            "If you are not in immediate danger, contact a local crisis hotline or a trusted person nearby for support."
        ),
        "actions": [
            "Call your local emergency number if immediate danger.",
            "Contact a local crisis hotline or a trusted person nearby.",
        ],
    },
    "redirect_support": {
        "level": "redirect_support",
        "title": "Support recommended",
        "message": (
            "I can’t help with this directly. If you are in immediate danger, call your local emergency number now. "
            "If you are not in immediate danger, consider contacting a local crisis hotline or a trusted person for support."
        ),
        "actions": [
            "Call your local emergency number if immediate danger.",
            "Contact a local crisis hotline or a trusted person.",
        ],
    },
    "support_overlay": {
        "level": "support_overlay",
        "title": "Support resources",
        "message": (
            "If you are in immediate danger, call your local emergency number now. "
            "If you are not in immediate danger, you can contact a local crisis hotline or reach out to a trusted person."
        ),
        "actions": [
            "Call your local emergency number if immediate danger.",
            "Contact a local crisis hotline or a trusted person.",
        ],
    },
}


def get_escalation_message(level: str) -> Dict[str, Any]:
    return LEVEL_TO_MESSAGE.get(level, {})
    