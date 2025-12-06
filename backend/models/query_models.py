from pydantic import BaseModel
from typing import List, Optional


class VerseItem(BaseModel):
    book: str
    chapter: int
    verse: int
    text: str


class QueryRequest(BaseModel):
    question: str
    translation: Optional[str] = "kjv"
    persona: Optional[str] = None
    want_commentary: bool = False


class QueryResponse(BaseModel):
    verses: List[VerseItem]
    summary: str
    commentary: Optional[str] = None
