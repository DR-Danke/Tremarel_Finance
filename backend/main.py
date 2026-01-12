"""
Finance Tracker - Backend Entry Point

FastAPI application for income/expense tracking with multi-entity support.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Finance Tracker API",
    description="Income/expense tracking for family and startup management",
    version="1.0.0",
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check() -> dict:
    """Health check endpoint for monitoring."""
    print("INFO [main]: Health check requested")
    return {"status": "healthy", "service": "finance-tracker-api"}


if __name__ == "__main__":
    import uvicorn
    print("INFO [main]: Starting Finance Tracker API server")
    uvicorn.run(app, host="0.0.0.0", port=8000)
