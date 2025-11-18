from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router as api_router

app = FastAPI(
    title="AI Candidate Evaluation System",
    description="Candidate evaluation pipeline with Gemini and Qdrant",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Main API endpoints
app.include_router(api_router, prefix="/api", tags=["evaluation"])

@app.get("/")
async def root():
    return {
        "message": "AI Candidate Evaluation System API",
        "version": "2.0.0",
        "description": "Gemini + Qdrant powered evaluation pipeline",
        "endpoints": {
            "evaluation": {
                "start": "/api/evaluate/start",
                "complete": "/api/evaluate/complete",
                "full": "/api/evaluate/full",
                "status": "/api/evaluate/status/{candidate_id}"
            }
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "2.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)