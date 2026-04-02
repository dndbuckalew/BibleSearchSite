# backend/backend_api_main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables early
load_dotenv()

app = FastAPI(
    title="Bible Therapy Assistant",
    description="Backend API wiring for the Bible Therapy Assistant",
    version="2.0.0",
)

# CORS (development-safe; tighten later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}
