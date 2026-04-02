# File: backend/escalation_router.py
# Purpose: Tier 0.5 deterministic escalation routing (NO messaging, NO reflection, NO scripture logic)

from __future__ import annotations

from typing import Dict, Optional, Literal

EscalationLevel = Literal["support_overlay", "redirect_support", "hard_stop"]

_ALLOWED_LEVELS = {"support_overlay", "redirect_support", "hard_stop"}


def route_escalation_level(
    *,
    crisis_type: Optional[str],
    confidence: Optional[float],
    route_map: Dict[str, str],
    high_conf_threshold: float = 0.85,
) -> Optional[str]:
    """
    Deterministically decide whether to set escalation_level.

    Rules (per Phase 9.8B.5):
    - If crisis_type is None/empty -> None
    - If confidence is None or < high_conf_threshold -> None (LOW confidence never escalates)
    - If crisis_type is not mapped -> None
    - If mapped value is not an allowed level -> None

    Returns:
      Optional[str] escalation_level (only): "support_overlay" | "redirect_support" | "hard_stop" | None
    """
    if not crisis_type:
        return None

    if confidence is None:
        return None

    # Normalize defensive: if confidence is out of [0,1], treat as non-escalating
    if confidence < 0.0 or confidence > 1.0:
        return None

    if confidence < high_conf_threshold:
        return None

    level = route_map.get(crisis_type)
    if not level:
        return None

    if level not in _ALLOWED_LEVELS:
        return None

    return level
    