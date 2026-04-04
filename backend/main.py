# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ------------------------------------------------------------------
# Routers (import only — do NOT include yet)
# ------------------------------------------------------------------

# Phase 9: WHY gate
from backend.api.query import router as query_router

# Phase 9.5: WHAT execution
from backend.api.results import router as results_router

# Other feature routers
from backend.routes.persona_routes import router as persona_router
from backend.routes.flipped_routes import router as flipped_router

# ------------------------------------------------------------------
# API OPENAI
# ------------------------------------------------------------------

from dotenv import load_dotenv
load_dotenv()

import os

print("===================================")
print("OPENAI KEY LOADED:", os.getenv("OPENAI_API_KEY") is not None)

key = os.getenv("OPENAI_API_KEY")

if key:
    print("OPENAI KEY PREFIX:", key[:10])
else:
    print("OPENAI KEY PREFIX: None")

print("===================================")

# ------------------------------------------------------------------
# App initialization
# ------------------------------------------------------------------

app = FastAPI(
    title="Bible Therapy Assistant",
    description="Production API for the Bible Therapy Assistant",
    version="2.0.0",
)

# ------------------------------------------------------------------
# CORS (relaxed for development; tighten for production later)
# ------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# Routers (order matters conceptually, not technically)
# ------------------------------------------------------------------

# WHY page — intent, guardrails, redirect logic
app.include_router(query_router, tags=["Query"])

# WHAT page — deterministic execution only
app.include_router(results_router, tags=["Results"])

# Persona selection
app.include_router(
    persona_router,
    prefix="/api/persona",
    tags=["Persona"],
)

# Flipped / reflective interaction routes
app.include_router(
    flipped_router,
    prefix="/api/flipped",
    tags=["Flipped Interaction"],
)

# ------------------------------------------------------------------
# Health check
# ------------------------------------------------------------------

@app.get("/health", tags=["default"])
def health_check():
    return {"status": "ok"}
