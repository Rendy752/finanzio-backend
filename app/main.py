# app/main.py

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.db import init_db
from app.api.v1.endpoints import router as api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    print("Application startup complete.")
    yield
    print("Application shutdown complete.")

app = FastAPI(
    title="Finanzio Backend API",
    version="1.0.0",
    description="Backend services for the multiplatform personal finance and SME bookkeeping application.",
    lifespan=lifespan
)
# ---------------------------------

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Finanzio API is running! Go to /docs for endpoints."}