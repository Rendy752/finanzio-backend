# app/main.py

from fastapi import FastAPI
from app.core.db import init_db
from app.api.v1.endpoints import router as api_router # Assuming you place registration logic here

app = FastAPI(
    title="Finanzio Backend API",
    version="1.0.0",
    description="Backend services for the multiplatform personal finance and SME bookkeeping application.",
)
# ---------------------------------

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Run database initialization on startup."""
    await init_db()

@app.get("/")
def read_root():
    return {"message": "Finanzio API is running! Go to /docs for endpoints."}
