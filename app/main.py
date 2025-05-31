from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.query_router import router as query_router

app = FastAPI(
    title="AI Research Assistant",
    description="Backend API for web-enabled AI research assistant",
    version="0.1.0"
)

# Allow all origins (for development only)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # allow all HTTP methods
    allow_headers=["*"],
)

# Include routes
app.include_router(query_router, prefix="/api")

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
