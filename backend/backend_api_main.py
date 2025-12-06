from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.query_service import fetch_verses_for_topic, summarize_and_contextualize

# ------------------------------------------------------------
# FastAPI App Initialization
# ------------------------------------------------------------

app = FastAPI(
    title="Biblical Therapy Assistant API",
    description="Backend for the Bible Therapy Assistant app.",
    version="1.0.0"
)

# ------------------------------------------------------------
# CORS Middleware (allows frontend to connect)
# ------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # You can restrict this later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------
# Request / Response Models
# ------------------------------------------------------------

class QueryRequest(BaseModel):
    question: str
    translation: str = "kjv"
    persona: str = "pastor"
    want_commentary: bool = True


class VerseItem(BaseModel):
    book: str
    chapter: int
    verse: int
    text: str


class QueryResponse(BaseModel):
    verses: list[VerseItem]
    summary: str = ""
    commentary: str = ""


# ------------------------------------------------------------
# Root Endpoint
# ------------------------------------------------------------

@app.get("/")
def root():
    return {"message": "Bible Therapy Assistant Backend is running."}


# ------------------------------------------------------------
# MAIN QUERY ENDPOINT
# ------------------------------------------------------------

@app.post("/api/query", response_model=QueryResponse)
def query_bible(req: QueryRequest):
    """
    Main endpoint: receives a question and returns:
      - relevant Bible verses,
      - a summary,
      - optional commentary.
    """
    try:
        # Step 1: Fetch verses
        verses_raw = fetch_verses_for_topic(
            topic=req.question,
            translation=req.translation,
        )

        if not verses_raw:
            raise HTTPException(status_code=404, detail="No verses found.")

        # Convert dicts → VerseItem objects
        verses = [VerseItem(**v) for v in verses_raw]

        # Step 2: Summarize + Contextualize
        summary_text, commentary_text = summarize_and_contextualize(
            question=req.question,
            verses=verses_raw,
            persona=req.persona,
            want_commentary=req.want_commentary
        )

        # Step 3: Return proper JSON structure
        return QueryResponse(
            verses=verses,
            summary=summary_text,
            commentary=commentary_text,
        )

    except Exception as e:
        print("❌ ERROR in /api/query:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
