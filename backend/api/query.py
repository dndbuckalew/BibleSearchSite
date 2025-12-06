from fastapi import APIRouter, HTTPException
from typing import Optional, List
from pydantic import BaseModel

from models.query_models import QueryRequest, QueryResponse

from services.query_service import (
    fetch_verses_for_topic,
    summarize_and_contextualize,
)

router = APIRouter()

@router.post("/api/query", response_model=QueryResponse)
def handle_query(req: QueryRequest):
    if not req.question or len(req.question.strip()) < 3:
        raise HTTPException(status_code=400, detail="Provide a clear question.")

    # Step 1: find verses
    verses = fetch_verses_for_topic(req.question, translation=req.translation)

    # Step 2: summarize + optional commentary
    summary, commentary = summarize_and_contextualize(
        req.question, verses, req.persona, req.want_commentary
    )

    result = {
        "verses": verses,
        "summary": summary,
        "commentary": commentary if req.want_commentary else None,
    }

    return result
