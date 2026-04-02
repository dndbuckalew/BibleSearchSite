from backend.models.persona_models import PersonaRequest, PersonaResponse


class PersonaService:
    """
    Phase 7.x Persona Service

    Responsibilities:
    - Accept persona selection
    - Return deterministic persona configuration
    - No AI behavior, no generation
    """

    def process_persona(self, req: PersonaRequest) -> PersonaResponse:
        persona = (req.persona or "pastoral").lower()

        if persona == "academic":
            tone = "Analytical, text-focused, historically grounded."
        elif persona == "devotional":
            tone = "Reflective, gentle, spiritually encouraging."
        else:
            tone = "Pastoral, compassionate, and thoughtful."

        return PersonaResponse(
            persona=persona,
            description=tone
        )
