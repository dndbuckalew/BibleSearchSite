# backend/models/persona_models.py

from pydantic import BaseModel
from typing import Optional

class PersonaRequest(BaseModel):
    persona: str
    question: str
    want_commentary: Optional[bool] = False

class PersonaResponse(BaseModel):
    persona: str
    input_question: str
    response: str
