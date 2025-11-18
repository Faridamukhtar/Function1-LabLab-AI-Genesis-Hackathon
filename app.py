import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.api import app_router

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AI Micro-Apprenticeship Platform",
    description="AI-powered candidate evaluation system",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(app_router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "AI Micro-Apprenticeship Platform"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)