import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.models.query_models import QueryRequest, QueryResponse
from backend.services.query_service import QueryService

from dotenv import load_dotenv
load_dotenv()


# ------------------------------------------------------
# App initialization
# ------------------------------------------------------
app = FastAPI(
    title="Biblical Therapy Assistant API",
    description="Backend for the Bible Therapy Assistant app.",
    version="1.0.0"
)

@app.get("/api/tester-info")
def tester_info():
    """
    Exposes non-sensitive tester configuration.
    Password is NEVER returned.
    """
    return {
        "tester_user": os.getenv("BTA_TEST_USER")
    }

# ------------------------------------------------------
# CORS (Phase 4: permissive, tighten later)
# ------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------
# Service layer
# ------------------------------------------------------
query_service = QueryService()

# ------------------------------------------------------
# Root health check
# ------------------------------------------------------
@app.get("/")
def root():
    return {"status": "ok"}

# ------------------------------------------------------
# Main query endpoint
# ------------------------------------------------------
@app.post("/api/query", response_model=QueryResponse)
def query_bible(req: QueryRequest):
    """
    Main endpoint: receives a question and returns:
      - Bible verses (KJV for V1)
      - summary placeholder
      - optional commentary placeholder

    Phase 4:
    - API layer is thin
    - All logic delegated to QueryService
    """
    try:
        return query_service.process_query(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
