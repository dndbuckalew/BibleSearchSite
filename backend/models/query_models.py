from pydantic import BaseModel
from typing import List, Optional

class VerseItem(BaseModel):
    reference: str
    text: str

    testament: Optional[str] = None
    book_order: Optional[int] = None
    chapter: Optional[int] = None
    verse: Optional[int] = None

class QueryRequest(BaseModel):
    question: str
    translation: Optional[str] = "kjv"
    persona: Optional[str] = None
    want_commentary: bool = False

class QueryResponse(BaseModel):
    verses: List[VerseItem]
    summary: str
    commentary: Optional[str] = None
    context: Optional[str] = None
    reflection: Optional[str] = None



